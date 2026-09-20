import os
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2
from sqlalchemy.orm import Session
from backend.database import SessionLocal, Base, engine
from backend.models import GraphNodeModel, GraphEdgeModel
from backend.modules.module9_audit_ledger import AuditLedgerEngine

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
DOCS_DIR = os.path.join(STATIC_DIR, "documents")
FACES_DIR = os.path.join(STATIC_DIR, "faces")

os.makedirs(DOCS_DIR, exist_ok=True)
os.makedirs(FACES_DIR, exist_ok=True)

def generate_synthetic_passport_image(
    filename: str,
    country_code: str,
    country_name: str,
    doc_number: str,
    surname: str,
    given_names: str,
    nationality: str,
    dob_yymmdd: str,
    gender: str,
    exp_yymmdd: str,
    photo_color: tuple = (70, 130, 180),
    tamper_mode: str = "NONE" # "NONE", "ALTER_EXPIRY", "SPLICED_PHOTO"
) -> str:
    """Creates a synthetic passport document image with security background, MRZ, and optional tamper artifacts."""
    filepath = os.path.join(DOCS_DIR, filename)
    width, height = 750, 500
    
    # Create base passport page with subtle security guilloche gradient
    img = Image.new("RGB", (width, height), (245, 243, 235))
    draw = ImageDraw.Draw(img)

    # Draw security guilloche wave background
    for y in range(0, height, 12):
        shade = 225 + int(15 * np.sin(y / 20.0))
        draw.line([(0, y), (width, y + int(8 * np.cos(y / 15.0)))], fill=(shade, shade - 5, shade + 8), width=1)
    
    for x in range(0, width, 18):
        draw.line([(x, 0), (x + int(10 * np.sin(x / 25.0)), height)], fill=(225, 228, 235), width=1)

    # Header Bar
    header_color = (25, 45, 80) if country_code != "RUS" else (110, 25, 30)
    draw.rectangle([(0, 0), (width, 65)], fill=header_color)
    draw.text((25, 12), f"PASSPORT / PASSEPORT — {country_name.upper()}", fill=(255, 255, 255))
    draw.text((25, 35), f"ISSUING STATE: {country_code}   |   DOC TYPE: P", fill=(200, 220, 255))
    draw.rectangle([(620, 15), (720, 50)], outline=(220, 180, 70), width=2)
    draw.text((630, 25), "ICAO 9303", fill=(220, 180, 70))

    # Photo Box
    photo_x, photo_y = 40, 90
    pw, ph = 180, 230
    draw.rectangle([(photo_x-3, photo_y-3), (photo_x+pw+3, photo_y+ph+3)], outline=(180, 180, 180), width=2)
    
    # Draw synthetic face avatar in photo box
    draw.rectangle([(photo_x, photo_y), (photo_x+pw, photo_y+ph)], fill=photo_color)
    # Head & Shoulders silhouette
    cx, cy = photo_x + pw // 2, photo_y + 90
    draw.ellipse([(cx-45, cy-55), (cx+45, cy+45)], fill=(235, 205, 180)) # head
    # Hair
    draw.ellipse([(cx-48, cy-65), (cx+48, cy-25)], fill=(50, 40, 35))
    # Eyes & details
    draw.ellipse([(cx-22, cy-15), (cx-12, cy-8)], fill=(40, 40, 40))
    draw.ellipse([(cx+12, cy-15), (cx+22, cy-8)], fill=(40, 40, 40))
    draw.arc([(cx-15, cy+10), (cx+15, cy+25)], start=0, end=180, fill=(160, 80, 80), width=3)
    # Torso/Shoulders
    draw.polygon([(photo_x+15, photo_y+ph), (cx-35, cy+50), (cx+35, cy+50), (photo_x+pw-15, photo_y+ph)], fill=(45, 60, 85))

    # If SPLICED_PHOTO tamper mode: add visible JPEG boundary mismatch and tint irregularity
    if tamper_mode == "SPLICED_PHOTO":
        draw.rectangle([(photo_x+5, photo_y+5), (photo_x+pw-5, photo_y+ph-5)], outline=(255, 100, 100), width=1)

    # Document Fields (Right Column)
    fx = 250
    fields = [
        ("SURNAME / NOM", surname),
        ("GIVEN NAMES / PRÉNOMS", given_names),
        ("NATIONALITY / NATIONALITÉ", nationality),
        ("DATE OF BIRTH / DATE DE NAISSANCE", f"{dob_yymmdd[4:6]}/{dob_yymmdd[2:4]}/19{dob_yymmdd[0:2]}" if int(dob_yymmdd[0:2]) > 30 else f"{dob_yymmdd[4:6]}/{dob_yymmdd[2:4]}/20{dob_yymmdd[0:2]}"),
        ("SEX / SEXE", gender),
        ("DOCUMENT NO. / NO DU PASSEPORT", doc_number),
        ("EXPIRATION DATE / DATE D'EXPIRATION", f"{exp_yymmdd[4:6]}/{exp_yymmdd[2:4]}/20{exp_yymmdd[0:2]}")
    ]

    fy = 85
    for label, val in fields:
        draw.text((fx, fy), label, fill=(110, 120, 135))
        
        # Tamper on expiration field:
        if tamper_mode == "ALTER_EXPIRY" and "EXPIRATION" in label:
            # Draw patched text with digital artifact box
            draw.rectangle([(fx-4, fy+14), (fx+220, fy+32)], fill=(255, 255, 240), outline=(220, 220, 190))
            draw.text((fx, fy+15), "28/12/2032 [ALTERED]", fill=(10, 10, 10))
        else:
            draw.text((fx, fy+15), val, fill=(15, 25, 45))
        fy += 44

    # MRZ Machine Readable Zone at Bottom
    mrz_bg_y = 390
    draw.rectangle([(0, mrz_bg_y), (width, height)], fill=(250, 250, 248), outline=(210, 210, 210))
    
    # Compute MRZ lines
    from backend.modules.module1_intake import compute_mrz_check_digit
    
    p_num_clean = doc_number.replace('<', '')[:9].ljust(9, '<')
    p_num_check = str(compute_mrz_check_digit(p_num_clean))
    
    dob_check = str(compute_mrz_check_digit(dob_yymmdd))
    exp_check = str(compute_mrz_check_digit(exp_yymmdd))
    
    comp_data = p_num_clean + p_num_check + dob_yymmdd + dob_check + exp_yymmdd + exp_check + ("<" * 14) + "<"
    comp_check = str(compute_mrz_check_digit(comp_data))

    name_field = f"{surname.replace(' ', '<')}<<{given_names.replace(' ', '<')}".ljust(39, '<')[:39]
    line1 = f"P<{country_code}{name_field}"
    line2 = f"{p_num_clean}{p_num_check}{nationality}{dob_yymmdd}{dob_check}{gender}{exp_yymmdd}{exp_check}{'<'*14}<{comp_check}"

    try:
        mrz_font = ImageFont.truetype("C:\\Windows\\Fonts\\consola.ttf", 20)
    except Exception:
        mrz_font = ImageFont.load_default()

    draw.text((25, mrz_bg_y + 18), line1, fill=(10, 10, 10), font=mrz_font)
    draw.text((25, mrz_bg_y + 50), line2, fill=(10, 10, 10), font=mrz_font)

    img.save(filepath, "JPEG", quality=95)
    return filepath

def generate_live_capture_photo(filename: str, photo_color: tuple = (70, 130, 180), angle_variation: int = 0) -> str:
    """Generates a live camera capture selfie photo."""
    filepath = os.path.join(FACES_DIR, filename)
    width, height = 300, 360
    img = Image.new("RGB", (width, height), (220, 225, 230))
    draw = ImageDraw.Draw(img)

    cx, cy = width // 2 + angle_variation, height // 2 - 20
    # Head
    draw.ellipse([(cx-65, cy-80), (cx+65, cy+70)], fill=(235, 205, 180))
    # Hair
    draw.ellipse([(cx-70, cy-95), (cx+70, cy-40)], fill=(50, 40, 35))
    # Eyes
    draw.ellipse([(cx-32, cy-20), (cx-18, cy-10)], fill=(40, 40, 40))
    draw.ellipse([(cx+18, cy-20), (cx+32, cy-10)], fill=(40, 40, 40))
    # Smile
    draw.arc([(cx-25, cy+18), (cx+25, cy+38)], start=0, end=180, fill=(160, 80, 80), width=3)
    # Live background lighting gradient & clothes
    draw.polygon([(20, height), (cx-55, cy+85), (cx+55, cy+85), (width-20, height)], fill=photo_color)
    # Add timestamp watermark
    draw.text((15, height - 25), "CAM-04 JFK-T4 [LIVE 2026-09-02]", fill=(120, 130, 140))

    img.save(filepath, "JPEG", quality=95)
    return filepath

def seed_identity_database():
    """Initializes tables, seeds the graph with 10 identity records and 2 conflict scenarios, and initializes audit ledger."""
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    # Clear existing graph nodes & edges to avoid duplicates on re-seed
    db.query(GraphEdgeModel).delete()
    db.query(GraphNodeModel).delete()
    db.commit()

    # Initialize Audit Ledger Genesis
    ledger = AuditLedgerEngine(db)

    print("--- Generating Synthetic Passport Documents & Live Photos ---")
    # 1. Arthur Pendelton (Clean)
    generate_synthetic_passport_image(
        filename="passport_arthur_clean.jpg",
        country_code="GBR",
        country_name="United Kingdom",
        doc_number="928192831",
        surname="PENDELTON",
        given_names="ARTHUR EDWARD",
        nationality="GBR",
        dob_yymmdd="820614",
        gender="M",
        exp_yymmdd="340210",
        photo_color=(60, 110, 160),
        tamper_mode="NONE"
    )
    generate_live_capture_photo("live_arthur.jpg", photo_color=(60, 110, 160))

    # 2. Marcus Vance (Tampered Expiry)
    generate_synthetic_passport_image(
        filename="passport_marcus_tampered.jpg",
        country_code="USA",
        country_name="United States of America",
        doc_number="772183912",
        surname="VANCE",
        given_names="MARCUS RAYMOND",
        nationality="USA",
        dob_yymmdd="881103",
        gender="M",
        exp_yymmdd="230514", # Expired in reality, tampered on doc
        photo_color=(80, 130, 90),
        tamper_mode="ALTER_EXPIRY"
    )
    generate_live_capture_photo("live_marcus.jpg", photo_color=(80, 130, 90))

    # 3. Elena Rostova (Historical Russian Passport)
    generate_synthetic_passport_image(
        filename="passport_elena_historical_rus.jpg",
        country_code="RUS",
        country_name="Russian Federation",
        doc_number="74892184",
        surname="ROSTOVA",
        given_names="ELENA DMITRIEVNA",
        nationality="RUS",
        dob_yymmdd="910412",
        gender="F",
        exp_yymmdd="260410",
        photo_color=(150, 70, 110),
        tamper_mode="NONE"
    )
    # 4. Elena Vance (Conflicting US Passport presented with same facial biometric)
    generate_synthetic_passport_image(
        filename="passport_elena_fracture_usa.jpg",
        country_code="USA",
        country_name="United States of America",
        doc_number="90281944",
        surname="VANCE",
        given_names="ELENA MARIE",
        nationality="USA",
        dob_yymmdd="940820", # Conflicting DOB (1994 vs 1991)
        gender="F",
        exp_yymmdd="340218",
        photo_color=(150, 70, 110), # EXACT same facial avatar colors & embeddings
        tamper_mode="NONE"
    )
    generate_live_capture_photo("live_elena_shared.jpg", photo_color=(150, 70, 110))

    print("--- Seeding Identity Graph Nodes & Edges ---")

    # Helper function to add node and edge
    def add_n(node_id, ntype, label, props):
        n = GraphNodeModel(id=node_id, node_type=ntype, label=label, properties_json=json.dumps(props))
        db.add(n)

    def add_e(src, tgt, etype, props=None):
        e = GraphEdgeModel(source_id=src, target_id=tgt, edge_type=etype, properties_json=json.dumps(props or {}))
        db.add(e)

    # -------------------------------------------------------------------------
    # PERSONA 1: ARTHUR PENDELTON (Clean Identity Chain)
    # -------------------------------------------------------------------------
    add_n("person_arthur_pendelton", "PERSON", "Arthur Edward Pendelton", {
        "primary_name": "PENDELTON, ARTHUR EDWARD",
        "dob": "1982-06-14",
        "nationality": "GBR",
        "risk_status": "CLEAR",
        "cluster_id": "BIO-CLUSTER-001"
    })
    add_n("bio_arthur_cluster", "BIOMETRIC_EMBEDDING", "Arthur Pendelton Biometric DNA", {
        "cluster_id": "BIO-CLUSTER-001",
        "quality": 0.98,
        "enrolled_date": "2014-03-15"
    })
    add_n("pass_GBR_40192830", "PASSPORT", "UK Passport #GBR-40192830 (Expired 2024)", {
        "document_number": "GBR-40192830",
        "country": "GBR",
        "issue_date": "2014-03-15",
        "expiry_date": "2024-03-14",
        "status": "EXPIRED_SURRENDERED"
    })
    add_n("pass_GBR_928192831", "PASSPORT", "UK Passport #GBR-928192831 (Active)", {
        "document_number": "GBR-928192831",
        "country": "GBR",
        "issue_date": "2024-02-10",
        "expiry_date": "2034-02-09",
        "status": "ACTIVE"
    })
    add_n("visa_USA_B1B2", "VISA", "US B1/B2 10-Year Visa", {
        "visa_number": "V-USA-882910",
        "issuing_post": "London US Embassy",
        "valid_from": "2021-10-05",
        "valid_until": "2031-10-04",
        "entries": "MULTIPLE"
    })
    add_n("event_crossing_HND", "CROSSING_EVENT", "Border Entry: Tokyo Haneda", {
        "port": "HND", "date": "2017-07-22", "carrier": "BA007", "direction": "ENTRY"
    })
    add_n("event_crossing_JFK_prior", "CROSSING_EVENT", "Border Entry: New York JFK", {
        "port": "JFK", "date": "2022-11-04", "carrier": "VS003", "direction": "ENTRY"
    })

    # Edges for Arthur
    add_e("bio_arthur_cluster", "person_arthur_pendelton", "MATCHES_FACE")
    add_e("pass_GBR_40192830", "person_arthur_pendelton", "ISSUED_TO")
    add_e("pass_GBR_928192831", "person_arthur_pendelton", "ISSUED_TO")
    add_e("visa_USA_B1B2", "person_arthur_pendelton", "ISSUED_TO")
    add_e("person_arthur_pendelton", "event_crossing_HND", "TRAVELLED_ON")
    add_e("person_arthur_pendelton", "event_crossing_JFK_prior", "TRAVELLED_ON")

    # -------------------------------------------------------------------------
    # PERSONA 2: MARCUS VANCE (Tampered Document)
    # -------------------------------------------------------------------------
    add_n("person_marcus_vance", "PERSON", "Marcus Raymond Vance", {
        "primary_name": "VANCE, MARCUS RAYMOND",
        "dob": "1988-11-03",
        "nationality": "USA",
        "risk_status": "FORENSIC_FLAG"
    })
    add_n("bio_marcus_cluster", "BIOMETRIC_EMBEDDING", "Marcus Vance Biometrics", {
        "cluster_id": "BIO-CLUSTER-002",
        "quality": 0.95
    })
    add_n("pass_USA_772183912", "PASSPORT", "US Passport #USA-772183912 (Tampered Expiry)", {
        "document_number": "USA-772183912",
        "country": "USA",
        "issue_date": "2013-05-15",
        "expiry_date": "2023-05-14",
        "tamper_detected": True
    })
    add_e("bio_marcus_cluster", "person_marcus_vance", "MATCHES_FACE")
    add_e("pass_USA_772183912", "person_marcus_vance", "ISSUED_TO")

    # -------------------------------------------------------------------------
    # PERSONA 3 & 4: THE IDENTITY FRACTURE CASE (Elena Rostova / Elena Vance)
    # -------------------------------------------------------------------------
    # Biometric Node shared across 2 distinct identities!
    add_n("bio_cluster_elena_shared", "BIOMETRIC_EMBEDDING", "Biometric Cluster #BIO-4921 (Shared Face)", {
        "cluster_id": "BIO-CLUSTER-4921",
        "quality": 0.99,
        "is_conflicting_node": True,
        "conflict_summary": "Biometric face vectors match across 2 legally contradictory personas"
    })

    # Historical Identity: Elena Rostova (Russian)
    add_n("person_elena_rostova", "PERSON", "Elena Dmitrievna Rostova [Historical]", {
        "primary_name": "ROSTOVA, ELENA DMITRIEVNA",
        "dob": "1991-04-12",
        "nationality": "RUS",
        "primary_doc_number": "RUS-74892184",
        "prior_issuance_authority": "GUVM Ministry of Internal Affairs Moscow",
        "last_seen_border": "Paris CDG (2023-11-14)",
        "is_conflicting_node": True
    })
    add_n("pass_RUS_74892184", "PASSPORT", "Russian Passport #RUS-74892184", {
        "document_number": "RUS-74892184",
        "country": "RUS",
        "issue_date": "2016-04-10",
        "expiry_date": "2026-04-09",
        "status": "HISTORICAL_ACTIVE",
        "is_conflicting_node": True
    })
    add_n("event_crossing_LHR_elena", "CROSSING_EVENT", "Crossing: London Heathrow (2021)", {
        "port": "LHR", "date": "2021-06-03", "direction": "ENTRY"
    })
    add_n("event_crossing_CDG_elena", "CROSSING_EVENT", "Crossing: Paris CDG Exit (2023)", {
        "port": "CDG", "date": "2023-11-14", "direction": "EXIT"
    })

    # Conflicting Identity: Elena Vance (Claimed USA Identity presenting today)
    add_n("person_elena_vance", "PERSON", "Elena Marie Vance [Current Presentation]", {
        "primary_name": "VANCE, ELENA MARIE",
        "dob": "1994-08-20", # 3 Year Age Shift!
        "nationality": "USA",
        "primary_doc_number": "USA-90281944",
        "is_conflicting_node": True
    })
    add_n("pass_USA_90281944", "PASSPORT", "US Passport #USA-90281944 (Fracture Origin)", {
        "document_number": "USA-90281944",
        "country": "USA",
        "issue_date": "2024-02-18",
        "expiry_date": "2034-02-17",
        "is_conflicting_node": True
    })

    # Edges wiring the Fracture
    add_e("bio_cluster_elena_shared", "person_elena_rostova", "MATCHES_FACE", {"match_confidence": 0.98})
    add_e("bio_cluster_elena_shared", "person_elena_vance", "MATCHES_FACE", {"match_confidence": 0.98})
    add_e("pass_RUS_74892184", "person_elena_rostova", "ISSUED_TO")
    add_e("pass_USA_90281944", "person_elena_vance", "ISSUED_TO")
    add_e("person_elena_rostova", "event_crossing_LHR_elena", "TRAVELLED_ON")
    add_e("person_elena_rostova", "event_crossing_CDG_elena", "TRAVELLED_ON")
    add_e("person_elena_vance", "person_elena_rostova", "LINKED_TO", {
        "relationship": "CRITICAL_BIOMETRIC_COLLISION",
        "alert": "Contradictory Legal Identity under Same Face"
    })

    # -------------------------------------------------------------------------
    # PERSONAS 5-10: Additional Seed Travelers
    # -------------------------------------------------------------------------
    seed_travelers = [
        ("person_sofia_chen", "Sofia Chen", "CAN", "CAN-88192019", "1990-09-25"),
        ("person_liam_oconnor", "Liam O'Connor", "IRL", "IRL-55102948", "1985-02-18"),
        ("person_mateo_silva", "Mateo Silva", "BRA", "BRA-33109281", "1993-12-01"),
        ("person_amara_diallo", "Amara Diallo", "FRA", "FRA-66291048", "1987-05-19"),
        ("person_tariq_mansoor", "Tariq Al-Mansoor", "ARE", "ARE-99201844", "1980-07-30"),
        ("person_yulia_petrova", "Yulia Petrova", "EST", "EST-11928401", "1996-03-14")
    ]

    for p_id, name, nat, doc_num, dob in seed_travelers:
        add_n(p_id, "PERSON", name, {"primary_name": name, "nationality": nat, "dob": dob, "primary_doc_number": doc_num})
        doc_node = f"doc_{doc_num}"
        add_n(doc_node, "PASSPORT", f"{nat} Passport #{doc_num}", {"document_number": doc_num, "country": nat, "status": "ACTIVE"})
        add_e(doc_node, p_id, "ISSUED_TO")

    db.commit()
    print("[OK] Successfully initialized Identity Continuum database & seed graph with 10 identities.")

    # Embed photorealistic portraits into seeded passport documents
    try:
        from backend.scripts.update_demo_assets import update_assets
        update_assets()
    except Exception as e:
        print(f"[SEED WARNING] update_assets: {e}")

    # Record Seed Audit Block
    ledger.append_event("SYSTEM_SEED_COMPLETED", {
        "status": "SUCCESS",
        "identities_seeded": 10,
        "fracture_scenarios": 2,
        "jurisdiction": "GLOBAL_BORDER_DEFENSE_CONSORTIUM"
    })

    db.close()

if __name__ == "__main__":
    seed_identity_database()
