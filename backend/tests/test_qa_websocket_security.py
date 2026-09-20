import json
import base64
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

EXPECTED_SEQUENCE = [
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

def assert_standard_schema(msg: dict):
    """Verifies that every telemetry frame complies with versioned JSON schema."""
    assert "schema_version" in msg, "Missing schema_version"
    assert msg["schema_version"] == "2.1.0"
    assert "event" in msg, "Missing event"
    assert "session_id" in msg, "Missing session_id"
    assert "request_id" in msg, "Missing request_id"
    assert "progress" in msg, "Missing progress"
    assert "status" in msg, "Missing status"
    assert "message" in msg, "Missing message"
    assert "timestamp" in msg, "Missing timestamp"

def test_ws_clean_verification_full_sequence_and_schema():
    """Verify clean document execution, exact 9-step sequence, and real ledger block creation."""
    with client.websocket_connect("/ws/verification-stream") as ws:
        ws.send_json({"scenario": "clean"})
        events_received = []
        
        while True:
            msg = ws.receive_json()
            assert_standard_schema(msg)
            event = msg["event"]
            events_received.append(event)
            
            if event == "MODULE_9_AUDIT_LEDGER":
                assert msg["status"] == "COMPLETED"
                assert "block_index" in msg["data"]
                assert "block_hash" in msg["data"]
                assert msg["latency_ms"] > 0
                
            if event == "PIPELINE_COMPLETE":
                assert msg["progress"] == 100
                res = msg["data"]["result"]
                assert res["trust_evaluation"]["identity_trust_score"] > 90
                assert res["trust_evaluation"]["is_trust_chain_intact"] is True
                assert res["forensics"]["is_tampered"] is False
                assert res["audit_block_index"] > 0
                break

        assert events_received == EXPECTED_SEQUENCE, f"Sequence mismatch: {events_received}"

def test_ws_tampered_scenario_forensic_detection():
    """Verify tampered scenario flags ELA/Forensics and breaks trust chain."""
    with client.websocket_connect("/ws/verification-stream") as ws:
        ws.send_json({"scenario": "tampered"})
        while True:
            msg = ws.receive_json()
            assert_standard_schema(msg)
            if msg["event"] == "MODULE_5_FORENSICS":
                assert msg["status"] == "ANOMALY_DETECTED"
                assert msg["data"]["is_tampered"] is True
                assert msg["data"]["tampering_score"] >= 50.0
            if msg["event"] == "PIPELINE_COMPLETE":
                res = msg["data"]["result"]
                assert res["trust_evaluation"]["is_trust_chain_intact"] is False
                assert res["trust_evaluation"]["broken_layer"] == "Document Authenticity"
                break

def test_ws_face_mismatch_scenario():
    """Verify face mismatch scenario properly flags biometric broken layer."""
    with client.websocket_connect("/ws/verification-stream") as ws:
        ws.send_json({"scenario": "face_mismatch"})
        while True:
            msg = ws.receive_json()
            assert_standard_schema(msg)
            if msg["event"] == "MODULE_6_BIOMETRICS":
                assert msg["data"]["match_confidence"] < 50.0
            if msg["event"] == "PIPELINE_COMPLETE":
                res = msg["data"]["result"]
                assert res["trust_evaluation"]["is_trust_chain_intact"] is False
                assert res["trust_evaluation"]["broken_layer"] == "Person-Document Match"
                break

def test_ws_corrupted_image_handling():
    """Verify corrupted / unreadable binary image is safely rejected without server crash."""
    corrupted_b64 = "data:image/jpeg;base64," + base64.b64encode(b"NOT_A_VALID_JPEG_HEADER_CORRUPTED_STREAM").decode()
    with client.websocket_connect("/ws/verification-stream") as ws:
        ws.send_json({
            "doc_photo_base64": corrupted_b64,
            "scenario": "custom"
        })
        msg = ws.receive_json()
        assert msg["event"] == "ERROR"
        assert msg["error"] == "UNREADABLE_IMAGE_FORMAT"
        assert msg["status"] == "FAILED"

def test_ws_oversized_payload_handling():
    """Verify oversized payload (>10MB) is rejected with 422/ERROR."""
    fake_huge_b64 = "data:image/jpeg;base64," + ("A" * (15 * 1024 * 1024))
    with client.websocket_connect("/ws/verification-stream") as ws:
        ws.send_json({
            "doc_photo_base64": fake_huge_b64,
            "scenario": "custom"
        })
        msg = ws.receive_json()
        assert msg["event"] == "ERROR"
        assert msg["error"] == "PAYLOAD_TOO_LARGE"

def test_ws_malformed_json_handling():
    """Verify sending malformed non-JSON text returns an error message gracefully."""
    with client.websocket_connect("/ws/verification-stream") as ws:
        ws.send_text("THIS IS NOT JSON {{{{{")
        msg = ws.receive_json()
        assert msg["event"] == "ERROR"
        assert msg["error"] == "MALFORMED_JSON"

def test_ws_duplicate_request_id_prevention():
    """Verify duplicate client-supplied request_id is rejected on reconnect to prevent duplicate blocks."""
    custom_req_id = "VER-DEDUP-TEST-992"
    with client.websocket_connect("/ws/verification-stream") as ws:
        ws.send_json({"scenario": "clean", "request_id": custom_req_id})
        while True:
            msg = ws.receive_json()
            if msg["event"] == "PIPELINE_COMPLETE":
                break

        # Re-send same request_id in same session
        ws.send_json({"scenario": "clean", "request_id": custom_req_id})
        dup_msg = ws.receive_json()
        assert dup_msg["event"] == "ERROR"
        assert dup_msg["error"] == "DUPLICATE_REQUEST_ID"

def test_ws_disconnect_resilience():
    """Verify client disconnecting abruptly mid-stream does not crash the backend."""
    with client.websocket_connect("/ws/verification-stream") as ws:
        ws.send_json({"scenario": "clean"})
        _ = ws.receive_json() # receive INIT
        ws.close() # forced abrupt close

    # Verify server remains healthy
    health_res = client.get("/api/health")
    assert health_res.status_code == 200
    assert health_res.json()["status"] == "ONLINE"

def test_rest_fallback_schema_parity():
    """Verify REST /api/verify response schema matches WebSocket result payload exactly."""
    rest_res = client.post("/api/verify", json={"scenario": "clean"})
    assert rest_res.status_code == 200
    rest_data = rest_res.json()
    
    with client.websocket_connect("/ws/verification-stream") as ws:
        ws.send_json({"scenario": "clean"})
        while True:
            msg = ws.receive_json()
            if msg["event"] == "PIPELINE_COMPLETE":
                ws_result = msg["data"]["result"]
                break

    # Check matching core keys
    core_keys = ["verification_id", "scenario", "total_latency_ms", "intake", "validation", "forensics", "face_match", "second_look", "fracture_detected", "continuity", "trust_evaluation", "subgraph"]
    for k in core_keys:
        assert k in rest_data, f"Key {k} missing in REST response"
        assert k in ws_result, f"Key {k} missing in WS response"
