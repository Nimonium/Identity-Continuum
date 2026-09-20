import json
from fastapi.testclient import TestClient
from backend.main import app

def test_websocket_verification_stream():
    client = TestClient(app)
    with client.websocket_connect("/ws/verification-stream") as ws:
        ws.send_json({"scenario": "clean"})
        received_events = []
        while True:
            data = ws.receive_json()
            event = data.get("event")
            received_events.append(event)
            progress = data.get("progress")
            latency = data.get("latency_ms")
            summary = data.get("summary") or data.get("message") or ""
            print(f"[{event}] {progress}% | Latency: {latency}ms | {summary}")
            if event == "PIPELINE_COMPLETE":
                res = data.get("data", {}).get("result") or data.get("result")
                print("\nTotal Latency:", data.get("latency_ms") or data.get("total_latency_ms"), "ms")
                assert res["trust_evaluation"]["identity_trust_score"] > 90
                break
        
        expected = [
            "INIT",
            "MODULE_1_OCR",
            "MODULE_2_VALIDATOR",
            "MODULE_5_FORENSICS",
            "MODULE_6_BIOMETRICS",
            "MODULE_3_4_CONTINUITY_GRAPH",
            "MODULE_7_TRUST_ENGINE",
            "MODULE_9_AUDIT_LEDGER",
            "PIPELINE_COMPLETE"
        ]
        for exp in expected:
            assert exp in received_events, f"Missing expected event: {exp}"

    print("\n✅ WEBSOCKET TEST PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_websocket_verification_stream()
