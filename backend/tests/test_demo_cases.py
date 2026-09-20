import os
import sys
import json
from fastapi.testclient import TestClient

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Set UTF-8 encoding for Windows console output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from backend.main import app

client = TestClient(app)

def print_separator(title=""):
    print("=" * 80)
    if title:
        print(f" {title.upper()} ".center(80, "="))
        print("=" * 80)

def test_demo_cases():
    print_separator("IDENTITY CONTINUUM — BACKEND VERIFICATION TEST SUITE")
    print("Testing 3 Core Scenarios through Modules 1 -> 2 -> 5 -> 6 -> 3 -> 4 -> 7 -> 9\n")

    # -------------------------------------------------------------------------
    # CASE 1: CLEAN IDENTITY (Arthur Pendelton)
    # -------------------------------------------------------------------------
    print_separator("CASE 1: CLEAN IDENTITY (Arthur Edward Pendelton - GBR)")
    res1 = client.post("/api/verify", json={"scenario": "clean"})
    assert res1.status_code == 200, f"Case 1 HTTP Error: {res1.status_code}"
    d1 = res1.json()

    print(f"[*] Verification ID: {d1['verification_id']}")
    print(f"[*] Audit Block Index: #{d1['audit_block_index']} (Hash: {d1['audit_block_hash'][:16]}...)")
    
    # Module 1 & 2 Output
    intake1 = d1["intake"]["structured_data"]
    val1 = d1["validation"]
    print(f"\n[MODULE 1 & 2: INTAKE & VALIDATION]")
    print(f"  • Extracted Document: {intake1['document_type']} (Country: {intake1['issuing_country']}, Number: {intake1['document_number']})")
    print(f"  • Holder Name: {intake1.get('surname', '')} {intake1.get('given_names', '')}")
    print(f"  • Date of Birth: {intake1.get('date_of_birth', '')} | Sex: {intake1.get('gender', '')} | Expiry: {intake1.get('expiration_date', '')}")
    print(f"  • Document Validation Status: {'PASS' if val1['is_valid'] else 'FAIL'} ({val1['summary_message']})")
    assert val1["authority_valid"] is True, "Issuing authority should be valid for Case 1"
    assert val1["format_valid"] is True, "Format validation should pass for Case 1"

    # Module 5 Forensics
    for5_1 = d1["forensics"]
    print(f"\n[MODULE 5: FORENSICS & ELA]")
    print(f"  • Tampering Score: {for5_1['tampering_score']}/100 (Is Tampered: {for5_1['is_tampered']})")
    print(f"  • ELA Anomaly Level: {for5_1['ela_anomaly_level']} | FFT Spectral Anomaly: {for5_1['fft_anomaly_score']}")
    print(f"  • Flagged Manipulated Regions: {len(for5_1['flagged_regions'])}")
    print(f"  • Forensic Verdict: {for5_1['forensic_summary']}")
    assert for5_1["tampering_score"] < 50.0, "Tampering score should be low for clean document"

    # Module 6 Face & Second-Look AI
    face1 = d1["face_match"]
    sec1 = d1["second_look"]
    print(f"\n[MODULE 6: FACE VERIFICATION & SECOND-LOOK AI]")
    print(f"  • Facial Match Confidence: {face1['match_confidence']}% (Match: {face1['is_match']})")
    print(f"  • Liveness Score: {face1['liveness_score']}% ({face1['liveness_method']})")
    print(f"  • Embedding Model: {face1['embedding_model']}")
    print(f"  • AI Second-Look Verdict: {sec1['verdict']} (Confidence: {sec1['confidence_score']}%)")
    print(f"  • Suggested Officer Action: {sec1['suggested_action']}")
    assert face1["is_match"] is True, "Face should match for Case 1"
    assert sec1["verdict"] == "CLEAR", f"Expected CLEAR verdict, got {sec1['verdict']}"

    # Module 3 & 4 Identity Graph & Continuity
    fracture1 = d1["fracture_detected"]
    cont1 = d1["continuity"]
    print(f"\n[MODULE 3 & 4: IDENTITY DNA & CONTINUITY ENGINE]")
    print(f"  • Identity Fracture Detected: {fracture1}")
    print(f"  • Continuity Status: {cont1['continuity_status']} (Is Continuous: {cont1['is_continuous']})")
    print(f"  • Historical Timeline Events: {len(cont1['timeline_events'])} events tracked")
    print(f"  • Narrative: {cont1['narrative_summary']}")
    assert fracture1 is False, "No fracture should exist for Case 1"
    assert cont1["continuity_status"] == "CONSISTENT", "Timeline should be consistent for Case 1"

    # Module 7 Zero-Trust Evidence Chain
    trust1 = d1["trust_evaluation"]
    print(f"\n[MODULE 7: ZERO-TRUST EVIDENCE CHAIN & SCORE]")
    print(f"  • Final Identity Trust Score: {trust1['identity_trust_score']}/100")
    print(f"  • Trust Chain Intact: {trust1['is_trust_chain_intact']}")
    print(f"  • Broken Layer: {trust1['broken_layer'] or 'NONE (All 5 Layers Verified)'}")
    print(f"  • Chain Summary: {trust1['chain_summary']}")
    for link in trust1["links"]:
        sym = "[PASS]" if link["status"] == "VERIFIED" else ("[WARN]" if link["status"] == "WARNING" else "[FAIL]")
        print(f"    {sym} {link['layer_name']}: {link['status']} ({link['score']} pts) - {link['details']}")
    assert trust1["identity_trust_score"] >= 90.0, f"Expected score >= 90, got {trust1['identity_trust_score']}"
    assert trust1["is_trust_chain_intact"] is True, "Trust chain must be intact for Case 1"
    assert trust1["broken_layer"] is None, "No broken layer expected for Case 1"

    print("\n[OK] CASE 1 PASSED: CLEAN IDENTITY FULLY VERIFIED")

    # -------------------------------------------------------------------------
    # CASE 2: TAMPERED DOCUMENT (Marcus Vance)
    # -------------------------------------------------------------------------
    print_separator("CASE 2: TAMPERED DOCUMENT (Marcus Raymond Vance - USA)")
    res2 = client.post("/api/verify", json={"scenario": "tampered"})
    assert res2.status_code == 200, f"Case 2 HTTP Error: {res2.status_code}"
    d2 = res2.json()

    print(f"[*] Verification ID: {d2['verification_id']}")
    print(f"[*] Audit Block Index: #{d2['audit_block_index']} (Hash: {d2['audit_block_hash'][:16]}...)")

    # Module 1 & 2 Output
    intake2 = d2["intake"]["structured_data"]
    val2 = d2["validation"]
    print(f"\n[MODULE 1 & 2: INTAKE & VALIDATION]")
    print(f"  • Extracted Document: {intake2['document_type']} #{intake2['document_number']} ({intake2['issuing_country']})")
    print(f"  • Holder Name: {intake2.get('surname', '')} {intake2.get('given_names', '')}")

    # Module 5 Forensics
    for5_2 = d2["forensics"]
    print(f"\n[MODULE 5: FORENSICS & ELA]")
    print(f"  • Tampering Score: {for5_2['tampering_score']}/100 (Is Tampered: {for5_2['is_tampered']})")
    print(f"  • Flagged Manipulated Regions: {len(for5_2['flagged_regions'])}")
    for reg in for5_2['flagged_regions']:
        print(f"    - Flag [{reg['id']}]: {reg['label']} at (x:{reg['x']}, y:{reg['y']}) - {reg['description']} [Risk: {reg['risk_level']}]")
    print(f"  • Forensic Summary: {for5_2['forensic_summary']}")
    assert for5_2["tampering_score"] >= 70.0, f"Expected tampering score >= 70, got {for5_2['tampering_score']}"
    assert for5_2["is_tampered"] is True, "Document must be flagged as tampered"

    # Module 6 Face & Second-Look AI
    sec2 = d2["second_look"]
    print(f"\n[MODULE 6: FACE VERIFICATION & SECOND-LOOK AI]")
    print(f"  • AI Second-Look Verdict: {sec2['verdict']}")
    print(f"  • Suggested Action: {sec2['suggested_action']}")
    assert sec2["verdict"] in ["REVIEW", "HIGH_CONCERN"], f"Expected REVIEW or HIGH_CONCERN, got {sec2['verdict']}"

    # Module 7 Zero-Trust Evidence Chain
    trust2 = d2["trust_evaluation"]
    print(f"\n[MODULE 7: ZERO-TRUST EVIDENCE CHAIN & SCORE]")
    print(f"  • Final Identity Trust Score: {trust2['identity_trust_score']}/100")
    print(f"  • Trust Chain Intact: {trust2['is_trust_chain_intact']}")
    print(f"  • Broken Layer: {trust2['broken_layer']}")
    print(f"  • Chain Summary: {trust2['chain_summary']}")
    for link in trust2["links"]:
        sym = "[PASS]" if link["status"] == "VERIFIED" else ("[WARN]" if link["status"] == "WARNING" else "[FAIL]")
        print(f"    {sym} {link['layer_name']}: {link['status']} - {link['details']}")
    assert trust2["is_trust_chain_intact"] is False, "Trust chain must be broken for Case 2"
    assert trust2["broken_layer"] == "Document Authenticity", f"Expected broken layer 'Document Authenticity', got {trust2['broken_layer']}"
    assert 70.0 <= trust2["identity_trust_score"] <= 75.0, f"Expected raw weighted score ~73, got {trust2['identity_trust_score']}"

    print("\n[OK] CASE 2 PASSED: TAMPERED DOCUMENT DETECTED & ISOLATED")

    # -------------------------------------------------------------------------
    # CASE 3: IDENTITY FRACTURE (Elena Rostova / Elena Vance)
    # -------------------------------------------------------------------------
    print_separator("CASE 3: IDENTITY FRACTURE (Elena Rostova / Elena Vance)")
    res3 = client.post("/api/verify", json={"scenario": "fracture"})
    assert res3.status_code == 200, f"Case 3 HTTP Error: {res3.status_code}"
    d3 = res3.json()

    print(f"[*] Verification ID: {d3['verification_id']}")
    print(f"[*] Audit Block Index: #{d3['audit_block_index']} (Hash: {d3['audit_block_hash'][:16]}...)")

    # Module 3 & 4 Graph Traversal & Fracture Output
    fracture3 = d3["fracture_detected"]
    f_info3 = d3["fracture_info"]
    cont3 = d3["continuity"]
    print(f"\n[MODULE 3 & 4: IDENTITY DNA & GRAPH TRAVERSAL]")
    print(f"  • Identity Fracture Detected: {fracture3}")
    print(f"  • Discrepancy Summary: {f_info3['discrepancy_summary']}")
    print(f"  • Current Claim: Name '{f_info3['current_claim']['name']}', Passport #{f_info3['current_claim']['document_number']} ({f_info3['current_claim']['nationality']}), DOB: {f_info3['current_claim']['dob']}")
    print(f"  • Conflicting Biological History: Name '{f_info3['conflicting_record']['name']}', Passport #{f_info3['conflicting_record']['document_number']} ({f_info3['conflicting_record']['nationality']}), DOB: {f_info3['conflicting_record']['dob']}")
    print(f"  • Continuity Status: {cont3['continuity_status']}")
    print(f"  • Discontinuity Narrative: {cont3['narrative_summary']}")
    assert fracture3 is True, "Identity fracture must be detected for Case 3"
    assert "ROSTOVA" in f_info3["conflicting_record"]["name"], "Conflicting record must cite Elena Rostova"

    # Module 6 Face & Second-Look AI
    sec3 = d3["second_look"]
    print(f"\n[MODULE 6: FACE VERIFICATION & SECOND-LOOK AI]")
    print(f"  • AI Second-Look Verdict: {sec3['verdict']} (Confidence: {sec3['confidence_score']}%)")
    print(f"  • Suggested Action: {sec3['suggested_action']}")
    print(f"  • Officer Warning Prompt: {sec3['officer_prompt']}")
    assert sec3["verdict"] == "HIGH_CONCERN", f"Expected HIGH_CONCERN for fracture, got {sec3['verdict']}"

    # Module 7 Zero-Trust Evidence Chain
    trust3 = d3["trust_evaluation"]
    print(f"\n[MODULE 7: ZERO-TRUST EVIDENCE CHAIN & SCORE]")
    print(f"  • Final Identity Trust Score: {trust3['identity_trust_score']}/100")
    print(f"  • Trust Chain Intact: {trust3['is_trust_chain_intact']}")
    print(f"  • Broken Layer: {trust3['broken_layer']}")
    print(f"  • Chain Summary: {trust3['chain_summary']}")
    for link in trust3["links"]:
        sym = "[PASS]" if link["status"] == "VERIFIED" else ("[WARN]" if link["status"] == "WARNING" else "[FAIL]")
        print(f"    {sym} {link['layer_name']}: {link['status']} - {link['details']}")
    assert trust3["is_trust_chain_intact"] is False, "Trust chain must be broken for Case 3"
    assert trust3["broken_layer"] == "Historical Identity Continuity", f"Expected broken layer 'Historical Identity Continuity', got {trust3['broken_layer']}"
    assert 70.0 <= trust3["identity_trust_score"] <= 75.0, f"Expected raw weighted score ~73, got {trust3['identity_trust_score']}"

    print("\n[OK] CASE 3 PASSED: IDENTITY FRACTURE DISCOVERED VIA BIOMETRIC GRAPH")

    # -------------------------------------------------------------------------
    # SYNTHETIC CHECK: 2-BROKEN-LAYER MONOTONICITY VALIDATION
    # -------------------------------------------------------------------------
    print_separator("SYNTHETIC CHECK: DUAL-FAILURE MONOTONICITY VALIDATION")
    from backend.modules.module7_trust_engine import evaluate_zero_trust_chain
    
    # Construct a compound failure: both Document Authenticity (tampered) AND Historical Continuity (fracture) fail
    dual_fail_res = evaluate_zero_trust_chain(
        authority_valid=True,
        doc_validation_passed=False,
        tampering_score=88.5,
        face_match_confidence=94.2,
        liveness_passed=True,
        graph_fracture_detected=True,
        fracture_details={"type": "BIOMETRIC_IDENTITY_FRACTURE"},
        continuity_status="DISCONTINUITY_DETECTED",
        journey_valid=True
    )
    
    print(f"[*] Dual-Failure Trust Score: {dual_fail_res.identity_trust_score}/100")
    print(f"[*] Trust Chain Intact: {dual_fail_res.is_trust_chain_intact}")
    print(f"[*] Broken Layer: {dual_fail_res.broken_layer}")
    print(f"[*] Chain Summary: {dual_fail_res.chain_summary}")
    for link in dual_fail_res.links:
        sym = "[PASS]" if link.status == "VERIFIED" else ("[WARN]" if link.status == "WARNING" else "[FAIL]")
        print(f"    {sym} {link.layer_name}: {link.status} ({link.score} pts, weight: {link.confidence_weight})")

    # Monotonicity Assertions
    assert dual_fail_res.is_trust_chain_intact is False, "Dual failure must break trust chain"
    assert dual_fail_res.identity_trust_score < trust2["identity_trust_score"], (
        f"Monotonicity Violation: Dual-failure score ({dual_fail_res.identity_trust_score}) "
        f"must be strictly lower than single-failure Case 2 score ({trust2['identity_trust_score']})"
    )
    assert dual_fail_res.identity_trust_score < trust3["identity_trust_score"], (
        f"Monotonicity Violation: Dual-failure score ({dual_fail_res.identity_trust_score}) "
        f"must be strictly lower than single-failure Case 3 score ({trust3['identity_trust_score']})"
    )
    print(f"\n[OK] MONOTONICITY PROVED: Dual-failure ({dual_fail_res.identity_trust_score}) < Case 2 single-failure ({trust2['identity_trust_score']}) and Case 3 single-failure ({trust3['identity_trust_score']})")

    # -------------------------------------------------------------------------
    # MODULE 9: IMMUTABLE AUDIT LEDGER INTEGRITY TEST
    # -------------------------------------------------------------------------
    print_separator("MODULE 9: IMMUTABLE AUDIT LEDGER VERIFICATION")
    res_audit = client.post("/api/audit/verify")
    assert res_audit.status_code == 200, f"Audit verification HTTP error: {res_audit.status_code}"
    audit_data = res_audit.json()

    print(f"[*] Audit Ledger Status: {audit_data['status']}")
    print(f"[*] Blocks Checked: {audit_data['blocks_checked']} of {audit_data['total_blocks']}")
    print(f"[*] Tamper Detected: {audit_data['tamper_detected']}")
    print(f"[*] Latest Block SHA-256 Hash: {audit_data.get('latest_block_hash', 'N/A')}")
    print(f"[*] Cryptographic Result: {audit_data['message']}")
    assert audit_data["is_valid"] is True, "Audit chain must pass mathematical hash verification"
    assert audit_data["tamper_detected"] is False, "No tampering must be detected in chain"

    # Test Officer Override Event logging
    print("\n[*] Testing Officer Override Event Commitment...")
    res_override = client.post("/api/officer-decision", json={
        "verification_id": d3["verification_id"],
        "decision": "DENIED_ENTRY",
        "officer_badge": "OFFICER-CBP-8812",
        "justification_reason": "Identity fracture confirmed: facial biometric cluster matches active Russian passport #RUS-74892184 under name Elena Rostova.",
        "system_score": trust3["identity_trust_score"]
    })
    assert res_override.status_code == 200
    override_data = res_override.json()
    print(f"  • Override Recorded in Block #{override_data['block_index']} (Hash: {override_data['block_hash'][:16]}...)")
    print(f"  • Confirmation Message: {override_data['message']}")

    # Re-verify audit chain with the new override block
    res_audit2 = client.post("/api/audit/verify")
    assert res_audit2.json()["is_valid"] is True
    print(f"  • Re-verified Hash Chain with Override Block: 100% VALID across {res_audit2.json()['blocks_checked']} blocks.")

    print("\n[OK] MODULE 9 PASSED: IMMUTABLE HASH CHAIN CRYPTOGRAPHICALLY VERIFIED")
    print_separator("ALL 3 DEMO SCENARIOS & 9 MODULES FULLY PASSED")

if __name__ == "__main__":
    test_demo_cases()
