import json
import hashlib
import datetime
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from backend.models import AuditBlockModel

def compute_block_hash(block_index: int, timestamp: str, event_type: str, payload_json: str, prev_hash: str) -> str:
    """Computes SHA-256 hash for a block ensuring strict deterministic cryptographic chaining."""
    raw_str = f"{block_index}:{timestamp}:{event_type}:{payload_json}:{prev_hash}"
    return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()

class AuditLedgerEngine:
    def __init__(self, db_session: Session):
        self.db = db_session
        self.ensure_genesis_block()

    def ensure_genesis_block(self):
        """Creates the Genesis Block if the audit ledger is empty."""
        genesis = self.db.query(AuditBlockModel).filter_by(block_index=0).first()
        if not genesis:
            timestamp = "2026-09-01T00:00:00.000000Z"
            event_type = "GENESIS_BLOCK"
            payload = {
                "ledger_name": "Identity Continuum Permissioned Audit Ledger",
                "consensus_mode": "Single-Node Cryptographic Hash-Chained Simulation",
                "authority": "Border Security Intelligence Node #109",
                "crypto_standard": "SHA-256 Hash Chain",
                "status": "INITIALIZED"
            }
            payload_json = json.dumps(payload, sort_keys=True)
            prev_hash = "0" * 64
            block_hash = compute_block_hash(0, timestamp, event_type, payload_json, prev_hash)

            genesis_block = AuditBlockModel(
                block_index=0,
                timestamp=timestamp,
                event_type=event_type,
                payload_json=payload_json,
                prev_hash=prev_hash,
                block_hash=block_hash
            )
            self.db.add(genesis_block)
            self.db.commit()

    def get_latest_block(self) -> AuditBlockModel:
        return self.db.query(AuditBlockModel).order_by(AuditBlockModel.block_index.desc()).first()

    def append_event(self, event_type: str, payload: Dict[str, Any]) -> AuditBlockModel:
        """Appends a new immutable event to the hash chain with retry and rollback resilience."""
        import time
        for attempt in range(3):
            try:
                latest = self.db.query(AuditBlockModel).order_by(AuditBlockModel.block_index.desc()).first()
                new_index = (latest.block_index + 1) if latest else 0
                prev_hash = latest.block_hash if latest else ("0" * 64)
                timestamp = datetime.datetime.utcnow().isoformat() + "Z"
                payload_json = json.dumps(payload, sort_keys=True)
                
                block_hash = compute_block_hash(new_index, timestamp, event_type, payload_json, prev_hash)

                new_block = AuditBlockModel(
                    block_index=new_index,
                    timestamp=timestamp,
                    event_type=event_type,
                    payload_json=payload_json,
                    prev_hash=prev_hash,
                    block_hash=block_hash
                )
                self.db.add(new_block)
                self.db.commit()
                self.db.refresh(new_block)
                return new_block
            except Exception:
                self.db.rollback()
                if attempt == 2:
                    raise
                time.sleep(0.05)

    def get_audit_trail(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Returns the chronological or reverse-chronological list of audit blocks."""
        blocks = self.db.query(AuditBlockModel).order_by(AuditBlockModel.block_index.desc()).limit(limit).all()
        result = []
        for b in blocks:
            try:
                p = json.loads(b.payload_json)
            except Exception:
                p = {"raw": b.payload_json}

            result.append({
                "block_index": b.block_index,
                "timestamp": b.timestamp,
                "event_type": b.event_type,
                "payload": p,
                "prev_hash": b.prev_hash,
                "block_hash": b.block_hash,
                "short_hash": f"{b.block_hash[:8]}...{b.block_hash[-6:]}",
                "short_prev_hash": f"{b.prev_hash[:8]}...{b.prev_hash[-6:]}" if b.prev_hash != "0"*64 else "GENESIS_ROOT"
            })
        return result

    def verify_chain_integrity(self) -> Dict[str, Any]:
        """
        Scans and mathematically recalculates EVERY block in sequence from Genesis.
        Detects any tampering, payload edits, or broken hash pointers.
        """
        blocks = self.db.query(AuditBlockModel).order_by(AuditBlockModel.block_index.asc()).all()
        if not blocks:
            return {"is_valid": True, "blocks_checked": 0, "status": "EMPTY_CHAIN"}

        expected_prev_hash = "0" * 64
        verification_steps = []

        for b in blocks:
            # 1. Check prev_hash pointer
            if b.prev_hash != expected_prev_hash:
                return {
                    "is_valid": False,
                    "tamper_detected": True,
                    "failed_block_index": b.block_index,
                    "reason": f"Hash Pointer Mismatch at Block #{b.block_index}. Expected prev_hash '{expected_prev_hash[:12]}...', found '{b.prev_hash[:12]}...'",
                    "blocks_checked": len(verification_steps),
                    "total_blocks": len(blocks)
                }

            # 2. Recalculate block's own SHA-256 hash
            recomputed_hash = compute_block_hash(b.block_index, b.timestamp, b.event_type, b.payload_json, b.prev_hash)
            if recomputed_hash != b.block_hash:
                return {
                    "is_valid": False,
                    "tamper_detected": True,
                    "failed_block_index": b.block_index,
                    "reason": f"Cryptographic Signature Mismatch at Block #{b.block_index}. Content payload was altered. Stored: '{b.block_hash[:12]}...', Recomputed: '{recomputed_hash[:12]}...'",
                    "blocks_checked": len(verification_steps),
                    "total_blocks": len(blocks)
                }

            verification_steps.append({
                "block_index": b.block_index,
                "event_type": b.event_type,
                "hash_valid": True,
                "verified_hash": b.block_hash
            })
            expected_prev_hash = b.block_hash

        return {
            "is_valid": True,
            "tamper_detected": False,
            "blocks_checked": len(blocks),
            "total_blocks": len(blocks),
            "latest_block_hash": expected_prev_hash,
            "status": "CHAIN_INTEGRITY_VERIFIED_100_PERCENT",
            "message": f"Cryptographic verification passed across all {len(blocks)} immutable blocks. No tampering detected."
        }

    def record_officer_override(
        self, 
        verification_id: str, 
        officer_id: str, 
        decision: str, 
        reason: str,
        initial_score: float
    ) -> AuditBlockModel:
        """Records an officer decision / override as a first-class immutable block."""
        payload = {
            "action": "OFFICER_DECISION_RECORDED",
            "verification_id": verification_id,
            "officer_badge": officer_id,
            "decision": decision, # e.g. "CLEARED", "REFERRED_TO_SECONDARY", "DENIED_ENTRY"
            "justification_notes": reason,
            "initial_system_trust_score": initial_score,
            "jurisdiction": "US-CBP-JFK-T4"
        }
        return self.append_event("OFFICER_OVERRIDE_EVENT", payload)
