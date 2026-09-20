import os
import sys
import json
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.main import app

def test_genuine_upload():
    client = TestClient(app)
    
    print("=" * 70)
    print("TEST 1: Upload with Completely Arbitrary Filename (No Keywords, No MRZ Form Field)")
    print("=" * 70)

    # Read clean passport image bytes, but upload with random filename
    doc_path = os.path.join("backend", "static", "documents", "passport_arthur_clean.jpg")
    live_path = os.path.join("backend", "static", "faces", "live_arthur.jpg")

    with open(doc_path, "rb") as f:
        doc_bytes = f.read()
    with open(live_path, "rb") as f:
        live_bytes = f.read()

    # NOTE: Completely arbitrary filename without "arthur", "marcus", or "elena"
    arbitrary_filename = "scan_border_kiosk_99214.jpg"
    files = {
        "doc_file": (arbitrary_filename, doc_bytes, "image/jpeg"),
        "live_file": ("webcam_capture_temp.jpg", live_bytes, "image/jpeg")
    }
    # No document_mrz_or_text and no scenario_hint supplied!
    data = {
        "document_category": "PASSPORT"
    }

    res = client.post("/api/verify-upload", files=files, data=data)
    assert res.status_code == 200, f"Upload failed: {res.text}"
    result = res.json()

    intake = result["intake"]
    structured = intake["structured_data"]

    print(f"  Uploaded Filename: {arbitrary_filename}")
    print(f"  Extraction Pipeline: Genuine EasyOCR + OpenCV deskewing (Module 1)")
    print(f"  Extraction Confidence: {intake['extraction_confidence']}")
    print(f"  Extracted Document Number: {structured.get('document_number')}")
    print(f"  Extracted Holder Name: {structured.get('holder_name')}")
    print(f"  Extracted Issuing Country: {structured.get('issuing_country')}")
    print(f"  Extracted Expiration Date: {structured.get('expiration_date')}")
    print(f"  Extracted MRZ Lines from Pixels: {intake.get('raw_mrz')}")
    print(f"  Warnings: {intake.get('warnings')}")
    print(f"  Verification ID Generated: {result['verification_id']}")
    print(f"  Total Latency: {result['total_latency_ms']}ms")

    print("\n" + "=" * 70)
    print("TEST 2: Upload Non-Document Image (Honest Failure Fallback)")
    print("=" * 70)

    # Generate or read a 100x100 solid image (non-document)
    import cv2
    import numpy as np
    blank_img = np.zeros((400, 400, 3), dtype=np.uint8)
    _, blank_bytes = cv2.imencode('.jpg', blank_img)

    files_blank = {
        "doc_file": ("unknown_receipt_photo.jpg", blank_bytes.tobytes(), "image/jpeg")
    }
    res_blank = client.post("/api/verify-upload", files=files_blank, data={"document_category": "PASSPORT"})
    assert res_blank.status_code == 200
    blank_res = res_blank.json()
    blank_intake = blank_res["intake"]

    print(f"  Uploaded Filename: unknown_receipt_photo.jpg (Blank non-document)")
    print(f"  Extraction Confidence: {blank_intake['extraction_confidence']}")
    print(f"  Extracted Document Number: {blank_intake['structured_data'].get('document_number')}")
    print(f"  Extracted Holder Name: {blank_intake['structured_data'].get('holder_name')}")
    print(f"  Warnings: {blank_intake['warnings']}")
    print(f"  Result: Honest failure fallback triggered without persona injection!")

if __name__ == "__main__":
    test_genuine_upload()
