import hashlib
import os
import secrets
import datetime
from typing import Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from backend.models import OfficerModel

# Active in-memory session token cache: token -> session dict
# In production this could be Redis or JWT, but in-memory with DB backing is zero-dependency and lightning fast
OFFICER_SESSIONS: Dict[str, Dict[str, Any]] = {}
SESSION_LIFETIME_HOURS = 24

def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """Hashes a password using PBKDF2-HMAC-SHA256 with 100,000 iterations."""
    if not salt:
        salt = secrets.token_hex(16)
    pw_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    ).hex()
    return pw_hash, salt

def verify_password(password: str, salt: str, expected_hash: str) -> bool:
    """Verifies a plain-text password against a PBKDF2 salt and hash."""
    computed_hash, _ = hash_password(password, salt)
    return secrets.compare_digest(computed_hash, expected_hash)

def create_officer_session(officer: OfficerModel) -> str:
    """Creates a secure session token for an authenticated officer."""
    token = f"OFF-SEC-{secrets.token_urlsafe(32)}"
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(hours=SESSION_LIFETIME_HOURS)
    OFFICER_SESSIONS[token] = {
        "badge_id": officer.badge_id,
        "full_name": officer.full_name,
        "rank": officer.rank,
        "checkpoint": officer.checkpoint,
        "clearance_level": officer.clearance_level,
        "created_at": datetime.datetime.utcnow().isoformat(),
        "expires_at": expires_at.isoformat()
    }
    return token

def get_officer_session(token: str) -> Optional[Dict[str, Any]]:
    """Retrieves and validates an active officer session token."""
    if not token or token not in OFFICER_SESSIONS:
        return None
    session = OFFICER_SESSIONS[token]
    expires_at = datetime.datetime.fromisoformat(session["expires_at"])
    if datetime.datetime.utcnow() > expires_at:
        del OFFICER_SESSIONS[token]
        return None
    return session

def revoke_officer_session(token: str) -> bool:
    """Revokes an active session token upon officer logout."""
    if token in OFFICER_SESSIONS:
        del OFFICER_SESSIONS[token]
        return True
    return False

# Authorized default border control officers for demo & operational use
DEFAULT_OFFICERS = [
    {
        "badge_id": "OFF-2026",
        "full_name": "CAPTAIN R. VERMA",
        "password": "BorderSecure2026!",
        "rank": "Senior Border Security Inspector",
        "checkpoint": "DELHI-T3",
        "clearance_level": "LEVEL_3_SECURE"
    },
    {
        "badge_id": "SSB-0421",
        "full_name": "M. CHOURASIYA",
        "password": "BorderSecure2026!",
        "rank": "Senior Border Inspection Officer",
        "checkpoint": "PANITANKI",
        "clearance_level": "LEVEL_3_SECURE"
    },
    {
        "badge_id": "CBP-8819",
        "full_name": "SARAH JENKINS",
        "password": "BorderSecure2026!",
        "rank": "Supervisory Border Patrol Agent",
        "checkpoint": "JFK-T4",
        "clearance_level": "LEVEL_3_SECURE"
    },
    {
        "badge_id": "UKBF-1092",
        "full_name": "DAVID STERLING",
        "password": "BorderSecure2026!",
        "rank": "Senior Border Force Officer",
        "checkpoint": "LHR-T5",
        "clearance_level": "LEVEL_3_SECURE"
    }
]

def seed_default_officers(db: Session):
    """Ensures default authorized border officers exist in the database with secure hashed credentials."""
    for off in DEFAULT_OFFICERS:
        existing = db.query(OfficerModel).filter(OfficerModel.badge_id == off["badge_id"]).first()
        if not existing:
            pw_hash, salt = hash_password(off["password"])
            officer = OfficerModel(
                badge_id=off["badge_id"],
                full_name=off["full_name"],
                password_hash=pw_hash,
                salt=salt,
                rank=off["rank"],
                checkpoint=off["checkpoint"],
                clearance_level=off["clearance_level"],
                is_active=True
            )
            db.add(officer)
        else:
            # Ensure name and checkpoint match
            existing.full_name = off["full_name"]
            existing.checkpoint = off["checkpoint"]
            existing.rank = off["rank"]
            existing.clearance_level = off["clearance_level"]
    db.commit()
