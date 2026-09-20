import os
import time
import requests
import json

def run_benchmark():
    url = "http://127.0.0.1:8000/api/verify-upload"
    doc_path = os.path.join("backend", "static", "documents", "passport_arthur_clean.jpg")
    live_path = os.path.join("backend", "static", "faces", "live_arthur.jpg")

    with open(doc_path, "rb") as f:
        doc_bytes = f.read()
    with open(live_path, "rb") as f:
        live_bytes = f.read()

    arbitrary_filename = "scan_border_kiosk_99214.jpg"

    print("=" * 80)
    print("CONSECUTIVE UPLOAD BENCHMARK (Real document pixels, random filename)")
    print("Endpoint: POST /api/verify-upload")
    print(f"Document Image Size: {len(doc_bytes)} bytes | Live Selfie Size: {len(live_bytes)} bytes")
    print("=" * 80)

    for call_num in [1, 2]:
        files = {
            "doc_file": (arbitrary_filename, doc_bytes, "image/jpeg"),
            "live_file": ("webcam_capture_temp.jpg", live_bytes, "image/jpeg")
        }
        data = {
            "document_category": "PASSPORT"
        }

        t_start = time.perf_counter()
        resp = requests.post(url, files=files, data=data)
        client_elapsed_ms = round((time.perf_counter() - t_start) * 1000, 1)

        assert resp.status_code == 200, f"Call {call_num} failed: {resp.text}"
        res = resp.json()

        server_total_latency_ms = res.get("total_latency_ms")
        intake = res.get("intake", {})
        structured = intake.get("structured_data", {})
        breakdown = res.get("latency_breakdown_ms", {})
        module_times = res.get("module_latencies", {}) # check if present

        print(f"\n>>> CALL {call_num} RESULTS ({'First Call Post-Startup' if call_num == 1 else 'Second Call Immediately After'}):")
        print(f"  • Client Round-Trip Latency : {client_elapsed_ms} ms ({client_elapsed_ms/1000:.2f}s)")
        print(f"  • Server Pipeline Latency  : {server_total_latency_ms} ms")
        print(f"  • Extracted Document No.   : {structured.get('document_number')}")
        print(f"  • Extracted Holder Name    : {structured.get('holder_name')}")
        print(f"  • Extracted Country        : {structured.get('issuing_country')}")
        print(f"  • Extracted Expiration     : {structured.get('expiration_date')}")
        print(f"  • Confidence Score         : {intake.get('extraction_confidence')}")
        print(f"  • Raw MRZ Extracted        : {intake.get('raw_mrz')}")
        print(f"  • Verification Status      : {res.get('overall_status')}")
        print(f"  • Trust Score              : {res.get('composite_score')}")

        if breakdown:
            print(f"  • Latency Breakdown        : {breakdown}")

    print("\n" + "=" * 80)
    print("BENCHMARK COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    run_benchmark()
