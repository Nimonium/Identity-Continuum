import os
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

SCENARIOS = [
    {
        "id": "clean",
        "name": "Arthur Pendelton (Clean)",
        "doc_file": "passport_arthur_clean.jpg",
        "live_file": "live_arthur.jpg"
    },
    {
        "id": "tampered",
        "name": "Marcus Vance (Tampered)",
        "doc_file": "passport_marcus_tampered.jpg",
        "live_file": "live_marcus.jpg"
    },
    {
        "id": "fracture",
        "name": "Elena Vance (Fracture)",
        "doc_file": "passport_elena_fracture_usa.jpg",
        "live_file": "live_elena_shared.jpg"
    }
]

def run_preset(scenario_id):
    resp = requests.post(f"{BASE_URL}/api/verify", json={"scenario": scenario_id})
    assert resp.status_code == 200, f"Preset {scenario_id} failed: {resp.text}"
    return resp.json()

def run_upload(doc_file, live_file):
    doc_path = os.path.join("backend", "static", "documents", doc_file)
    live_path = os.path.join("backend", "static", "faces", live_file)
    with open(doc_path, "rb") as df, open(live_path, "rb") as lf:
        files = {
            "doc_file": ("uploaded_" + doc_file, df.read(), "image/jpeg"),
            "live_file": ("uploaded_" + live_file, lf.read(), "image/jpeg")
        }
        data = {"document_category": "PASSPORT"}
        resp = requests.post(f"{BASE_URL}/api/verify-upload", files=files, data=data)
        assert resp.status_code == 200, f"Upload failed: {resp.text}"
        return resp.json()

def extract_metrics(res):
    val = res.get("validation", {})
    forensics = res.get("forensics", {})
    face = res.get("face_match", {})
    cont = res.get("continuity", {})
    trust = res.get("trust_evaluation", {})
    chain_intact = trust.get("is_trust_chain_intact")
    overall_status = "TRUST_CHAIN_INTACT" if chain_intact else f"BROKEN ({trust.get('broken_layer')})"
    return {
        "overall_status": overall_status,
        "broken_layer": trust.get("broken_layer"),
        "composite_score": trust.get("identity_trust_score"),
        "doc_valid": val.get("is_valid"),
        "tampering_score": forensics.get("tampering_score"),
        "is_tampered": forensics.get("is_tampered"),
        "forensic_flags": forensics.get("flags", []),
        "face_confidence": face.get("match_confidence"),
        "face_is_match": face.get("is_match"),
        "fracture_detected": res.get("fracture_detected")
    }

def main():
    print("=" * 90)
    print("DEMO PRESET VS DIRECT MULTIPART UPLOAD PARITY BENCHMARK")
    print("=" * 90)

    for sc in SCENARIOS:
        print(f"\nEvaluating: {sc['name']}")
        print("-" * 60)
        preset_res = run_preset(sc["id"])
        upload_res = run_upload(sc["doc_file"], sc["live_file"])

        p_metrics = extract_metrics(preset_res)
        u_metrics = extract_metrics(upload_res)

        print(f"  Preset  -> Status: {p_metrics['overall_status']:<25} | Broken: {str(p_metrics['broken_layer']):<22} | Score: {p_metrics['composite_score']:<5} | Face: {p_metrics['face_confidence']}% | Tamper: {p_metrics['tampering_score']} | Fracture: {p_metrics['fracture_detected']}")
        print(f"  Upload  -> Status: {u_metrics['overall_status']:<25} | Broken: {str(u_metrics['broken_layer']):<22} | Score: {u_metrics['composite_score']:<5} | Face: {u_metrics['face_confidence']}% | Tamper: {u_metrics['tampering_score']} | Fracture: {u_metrics['fracture_detected']}")

        # Validate matching consistency
        face_diff = abs(p_metrics['face_confidence'] - u_metrics['face_confidence'])
        print(f"  => Face Confidence Delta: {face_diff:.2f}%")
        print(f"  => Status Match: {p_metrics['overall_status'] == u_metrics['overall_status']}")
        print(f"  => Broken Layer Match: {p_metrics['broken_layer'] == u_metrics['broken_layer']}")
        print(f"  => Fracture Match: {p_metrics['fracture_detected'] == u_metrics['fracture_detected']}")

    print("\n" + "=" * 90)
    print("PARITY BENCHMARK COMPLETE")

if __name__ == "__main__":
    main()
