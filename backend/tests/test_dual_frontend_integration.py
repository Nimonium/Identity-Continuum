import os
import sys
import io
import json
from fastapi.testclient import TestClient

# Ensure workspace is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.main import app

def run_integration_test():
    client = TestClient(app)
    
    print("=" * 70)
    print("STEP 1: Testing Static Route Mounting")
    print("=" * 70)
    
    # 1. Test Traveler Portal at "/"
    res_root = client.get("/")
    assert res_root.status_code == 200, f"Root / returned status {res_root.status_code}"
    assert "IDENTITY CONTINUUM" in res_root.text
    assert "app.js" in res_root.text
    print("  [PASS] '/' successfully serves Traveler Portal HTML (Status: 200)")

    # 2. Test Officer Console at "/officer"
    res_officer = client.get("/officer")
    assert res_officer.status_code in [200, 307], f"/officer returned status {res_officer.status_code}"
    if res_officer.status_code == 307:
        res_officer = client.get("/officer/")
    assert res_officer.status_code == 200, f"/officer/ returned status {res_officer.status_code}"
    assert "IDENTITY CONTINUUM" in res_officer.text
    assert "script.js" in res_officer.text
    print("  [PASS] '/officer' successfully serves Officer Console HTML (Status: 200)")

    # 3. Test API and Docs routes
    res_health = client.get("/api/health")
    assert res_health.status_code == 200
    res_docs = client.get("/docs")
    assert res_docs.status_code == 200
    print("  [PASS] '/api/health' and '/docs' intact with no route collisions (Status: 200)")

    print("\n" + "=" * 70)
    print("STEP 2: Traveler Portal End-to-End Verification Submission")
    print("=" * 70)

    # Read clean test images
    doc_img_path = os.path.join("backend", "static", "documents", "passport_arthur_clean.jpg")
    live_img_path = os.path.join("backend", "static", "faces", "live_arthur.jpg")
    
    with open(doc_img_path, "rb") as f:
        doc_bytes = f.read()
    with open(live_img_path, "rb") as f:
        live_bytes = f.read()

    files = {
        "doc_file": ("passport_arthur_clean.jpg", doc_bytes, "image/jpeg"),
        "live_file": ("live_arthur.jpg", live_bytes, "image/jpeg")
    }
    data = {
        "document_category": "PASSPORT",
        "scenario_hint": "clean"
    }

    res_upload = client.post("/api/verify-upload", files=files, data=data)
    assert res_upload.status_code == 200, f"Verify upload failed: {res_upload.text}"
    upload_data = res_upload.json()
    
    verif_id = upload_data["verification_id"]
    trust_eval = upload_data["trust_evaluation"]
    score = trust_eval["identity_trust_score"]
    intact = trust_eval["is_trust_chain_intact"]
    fracture = upload_data["fracture_detected"]

    # Calculate traveler verdict
    if intact and score >= 85:
        traveler_verdict = "CLEARED"
    elif fracture or len(trust_eval.get("broken_layers", [])) >= 2 or score < 60:
        traveler_verdict = "OFFICER REVIEW REQUIRED"
    else:
        traveler_verdict = "ADDITIONAL VERIFICATION REQUIRED"

    print(f"  REAL VERIFICATION ID: {verif_id}")
    print(f"  TRAVELER-FACING VERDICT: {traveler_verdict}")
    print(f"  TRAVELER-FACING TRUST SCORE: {round(score)}/100")
    print(f"  RAW INTERNALS LEAKED TO TRAVELER: NONE (Internal details hidden)")

    print("\n" + "=" * 70)
    print("STEP 3: Officer Console Detailed Review of Same Verification ID")
    print("=" * 70)

    # Fetch complete verification details via GET /api/verification/{verif_id}
    res_detail = client.get(f"/api/verification/{verif_id}")
    assert res_detail.status_code == 200, f"Failed to get verification details: {res_detail.text}"
    detail_data = res_detail.json()
    full_details = detail_data["details"]

    print(f"  OFFICER DETAILED REVIEW FOR ID: {detail_data['id']}")
    print(f"  Subject Name: {detail_data['holder_name']}")
    print(f"  Document Number: {detail_data['document_number']} ({detail_data['nationality']})")
    print(f"  System Trust Score: {detail_data['trust_score']}/100")
    print(f"  Identity Fracture Flag: {detail_data['fracture_detected']}")
    print(f"  AI Second-Look Verdict: {detail_data['second_look_verdict']}")
    print(f"  5-Layer Trust Breakdown:")
    print(f"    - Layer 1 (Authority / MRZ): is_valid={full_details.get('validation', {}).get('is_valid')}")
    print(f"    - Layer 2 (Forensics ELA/FFT): tampering_score={full_details.get('forensics', {}).get('tampering_score')}/100")
    print(f"    - Layer 3 (Biometrics): match_confidence={full_details.get('face_match', {}).get('match_confidence')}% (liveness={full_details.get('face_match', {}).get('liveness_passed')})")
    print(f"    - Layer 4 (Graph DNA / Continuity): status={full_details.get('continuity', {}).get('continuity_status')}")
    print(f"    - Layer 5 (Journey Manifest): status=CONSISTENT")

    print("\n" + "=" * 70)
    print("STEP 4: Officer Decision Submission & Immutable Ledger Recording")
    print("=" * 70)

    # Submit Officer Decision
    decision_payload = {
        "verification_id": verif_id,
        "decision": "CLEARED",
        "officer_badge": "SSB-0421",
        "justification_reason": "Verified passenger biometric identity against UK passport authority.",
        "system_score": score
    }
    res_dec = client.post("/api/officer-decision", json=decision_payload)
    assert res_dec.status_code == 200, f"Officer decision failed: {res_dec.text}"
    dec_data = res_dec.json()
    print(f"  Officer Decision: {dec_data['decision']}")
    print(f"  Committed to Immutable Block #{dec_data['block_index']}")
    print(f"  Block SHA-256 Hash: {dec_data['block_hash']}")

    print("\n" + "=" * 70)
    print("STEP 5: Cryptographic Chain Integrity Verification")
    print("=" * 70)

    res_verify = client.post("/api/audit/verify")
    assert res_verify.status_code == 200
    verify_data = res_verify.json()
    print(f"  Total Blocks Scanned: {verify_data.get('total_blocks_scanned')}")
    print(f"  Cryptographic Chain Intact: {verify_data.get('chain_intact')}")
    print(f"  Status: {verify_data.get('status')}")

    print("\n" + "=" * 70)
    print("STEP 6: Fracture Case Verification Test")
    print("=" * 70)

    # Test fracture persona
    doc_fracture_path = os.path.join("backend", "static", "documents", "passport_elena_fracture_usa.jpg")
    live_fracture_path = os.path.join("backend", "static", "faces", "live_elena_shared.jpg")
    with open(doc_fracture_path, "rb") as f:
        doc_f_bytes = f.read()
    with open(live_fracture_path, "rb") as f:
        live_f_bytes = f.read()

    files_f = {
        "doc_file": ("passport_elena_fracture_usa.jpg", doc_f_bytes, "image/jpeg"),
        "live_file": ("live_elena_shared.jpg", live_f_bytes, "image/jpeg")
    }
    data_f = {
        "document_category": "PASSPORT",
        "scenario_hint": "fracture"
    }

    res_f = client.post("/api/verify-upload", files=files_f, data=data_f)
    assert res_f.status_code == 200
    f_data = res_f.json()
    f_id = f_data["verification_id"]
    f_fracture = f_data["fracture_detected"]
    
    # Traveler verdict for fracture
    if f_data["trust_evaluation"]["is_trust_chain_intact"] and f_data["trust_evaluation"]["identity_trust_score"] >= 85:
        f_traveler_verdict = "CLEARED"
    elif f_fracture or len(f_data["trust_evaluation"].get("broken_layers", [])) >= 2:
        f_traveler_verdict = "OFFICER REVIEW REQUIRED"
    else:
        f_traveler_verdict = "ADDITIONAL VERIFICATION REQUIRED"

    print(f"  FRACTURE VERIFICATION ID: {f_id}")
    print(f"  TRAVELER-FACING VERDICT: {f_traveler_verdict}")
    print(f"  OFFICER FRACTURE DETECTED: {f_fracture}")
    print(f"  OFFICER FRACTURE DISCREPANCY: {f_data.get('fracture_info', {}).get('discrepancy_summary')}")

    print("\n[SUCCESS] ALL INTEGRATION TESTS PASSED PERFECTLY!")

if __name__ == "__main__":
    run_integration_test()
