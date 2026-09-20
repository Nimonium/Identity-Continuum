import io
import os
import sys
import time
import numpy as np
from PIL import Image
from fastapi.testclient import TestClient

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from backend.main import app

client = TestClient(app)

def print_sep(title=""):
    print("=" * 80)
    if title:
        print(f" {title.upper()} ".center(80, "="))
        print("=" * 80)

def test_edge_cases_and_error_handling():
    print_sep("EDGE CASE & ERROR HANDLING TEST SUITE")

    # 1. Test Zero-Byte / Empty File Upload
    print("\n[*] 1. Testing Zero-Byte Upload...")
    empty_bytes = b""
    res_empty = client.post(
        "/api/verify-upload",
        files={"doc_file": ("empty.jpg", empty_bytes, "image/jpeg")}
    )
    print(f"  • Response Status: {res_empty.status_code}")
    print(f"  • Error Detail: {res_empty.json()['detail']}")
    assert res_empty.status_code == 422, "Empty file must return HTTP 422"
    assert "Empty" in res_empty.json()["detail"]
    print("  [OK] Zero-byte file rejected cleanly with HTTP 422.")

    # 2. Test Unsupported / Corrupted File (Text file renamed to .jpg)
    print("\n[*] 2. Testing Corrupted / Non-Image File...")
    bad_bytes = b"This is a text file not an image."
    res_bad = client.post(
        "/api/verify-upload",
        files={"doc_file": ("fake_passport.jpg", bad_bytes, "image/jpeg")}
    )
    print(f"  • Response Status: {res_bad.status_code}")
    print(f"  • Error Detail: {res_bad.json()['detail']}")
    assert res_bad.status_code == 422, "Corrupted file must return HTTP 422"
    assert "Invalid or unreadable" in res_bad.json()["detail"]
    print("  [OK] Corrupted/unreadable file rejected cleanly with HTTP 422.")

    # 3. Test Blank / White Image (Non-document image)
    print("\n[*] 3. Testing Non-Document Blank Image...")
    blank_img = Image.new("RGB", (400, 300), (255, 255, 255))
    buf = io.BytesIO()
    blank_img.save(buf, format="JPEG")
    blank_bytes = buf.getvalue()

    res_blank = client.post(
        "/api/verify-upload",
        files={
            "doc_file": ("blank_white.jpg", blank_bytes, "image/jpeg"),
            "live_file": ("blank_live.jpg", blank_bytes, "image/jpeg")
        }
    )
    print(f"  • Response Status: {res_blank.status_code}")
    d_blank = res_blank.json()
    print(f"  • Trust Score: {d_blank['trust_evaluation']['identity_trust_score']}/100")
    print(f"  • Trust Chain Intact: {d_blank['trust_evaluation']['is_trust_chain_intact']}")
    print(f"  • Broken Layer: {d_blank['trust_evaluation']['broken_layer']}")
    print(f"  • Live Face Detected: {d_blank['face_match']['face_detected_live']}")
    print(f"  • AI Second-Look Verdict: {d_blank['second_look']['verdict']}")
    assert res_blank.status_code == 200, "Non-document image should process without 500 crashes"
    assert d_blank["trust_evaluation"]["is_trust_chain_intact"] is False
    assert d_blank["face_match"]["face_detected_live"] is False
    print("  [OK] Non-document image handled gracefully without 500 crash.")

    # 4. Test Live Photo with No Face Detected
    print("\n[*] 4. Testing Document Upload with No Face in Live Photo...")
    doc_path = os.path.join(os.path.dirname(__file__), "../static/documents/passport_arthur_clean.jpg")
    with open(doc_path, "rb") as f:
        valid_doc_bytes = f.read()

    # Generate a live capture of a wall texture (no face)
    wall_img = Image.new("RGB", (300, 300), (120, 120, 120))
    buf_wall = io.BytesIO()
    wall_img.save(buf_wall, format="JPEG")
    wall_bytes = buf_wall.getvalue()

    res_noface = client.post(
        "/api/verify-upload",
        files={
            "doc_file": ("passport.jpg", valid_doc_bytes, "image/jpeg"),
            "live_file": ("wall_no_face.jpg", wall_bytes, "image/jpeg")
        },
        data={
            "document_mrz_or_text": "P<GBRPENDELTON<<ARTHUR<EDWARD<<<<<<<<<<<<<<<\n9281928319GBR8206141M3402100<<<<<<<<<<<<<<<8"
        }
    )
    d_noface = res_noface.json()
    print(f"  • Response Status: {res_noface.status_code}")
    print(f"  • Live Face Detected: {d_noface['face_match']['face_detected_live']}")
    print(f"  • Biometric Confidence: {d_noface['face_match']['match_confidence']}%")
    print(f"  • Broken Layer: {d_noface['trust_evaluation']['broken_layer']}")
    print(f"  • AI Action: {d_noface['second_look']['suggested_action']}")
    assert d_noface["face_match"]["face_detected_live"] is False
    assert d_noface["trust_evaluation"]["broken_layer"] == "Person-Document Match"
    print("  [OK] Missing live face handled cleanly and flagged in Trust Chain.")

    # 5. Test Non-MRZ Document (Visa / Driving Permit fallback)
    print("\n[*] 5. Testing Document with No MRZ (Visa / Permit Layout)...")
    res_visa = client.post(
        "/api/verify-upload",
        files={"doc_file": ("permit.jpg", valid_doc_bytes, "image/jpeg")},
        data={
            "document_category": "VISA",
            "document_mrz_or_text": "VISA NO: V-USA-9920194\nHOLDER: DOE, JANE\nTYPE: B1/B2 TOURIST\nENTRIES: MULTIPLE\nPASSPORT: P88291048"
        }
    )
    d_visa = res_visa.json()
    print(f"  • Response Status: {res_visa.status_code}")
    print(f"  • Extracted Visa Number: {d_visa['intake']['structured_data']['document_number']}")
    print(f"  • Extracted Type: {d_visa['intake']['structured_data'].get('visa_type', 'N/A')}")
    print(f"  • Intake Warnings: {d_visa['intake']['warnings']}")
    assert res_visa.status_code == 200
    assert d_visa["intake"]["structured_data"]["document_number"] == "V-USA-9920194"
    print("  [OK] Non-MRZ document field parser handled successfully.")

    # 6. Benchmark Full Pipeline Latency
    print("\n[*] 6. Benchmarking Full Pipeline Latency (Modules 1-2-5-6-3-4-7-9)...")
    latencies = []
    for i in range(5):
        t_start = time.perf_counter()
        res_bench = client.post("/api/verify", json={"scenario": "clean"})
        lat_ms = (time.perf_counter() - t_start) * 1000.0
        latencies.append(lat_ms)
        print(f"  • Run #{i+1}: {lat_ms:.2f}ms (Total reported inside pipeline: {res_bench.json()['total_latency_ms']}ms)")

    avg_lat = sum(latencies) / len(latencies)
    print(f"\n[LATENCY REPORT] Average Full Verification Pipeline Latency: {avg_lat:.2f}ms ({avg_lat/1000.0:.3f}s)")
    assert avg_lat < 1000.0, f"Latency should be < 1.0s, was {avg_lat:.2f}ms"
    print("  [OK] Typical latency is ~70-150ms (well under the 3-4s budget threshold).")

    print_sep("ALL ERROR-HANDLING & LATENCY BENCHMARKS PASSED")

if __name__ == "__main__":
    test_edge_cases_and_error_handling()
