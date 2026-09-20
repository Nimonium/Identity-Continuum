import datetime
import json
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey
from backend.database import Base

class GraphNodeModel(Base):
    __tablename__ = "graph_nodes"

    id = Column(String(128), primary_key=True, index=True)
    node_type = Column(String(64), nullable=False, index=True) # PERSON, PASSPORT, VISA, BIOMETRIC, ISSUANCE_EVENT, CROSSING_EVENT
    label = Column(String(256), nullable=False)
    properties_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    @property
    def properties(self):
        try:
            return json.loads(self.properties_json) if self.properties_json else {}
        except Exception:
            return {}

class GraphEdgeModel(Base):
    __tablename__ = "graph_edges"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(String(128), ForeignKey("graph_nodes.id"), nullable=False, index=True)
    target_id = Column(String(128), ForeignKey("graph_nodes.id"), nullable=False, index=True)
    edge_type = Column(String(64), nullable=False, index=True) # PRESENTED, ISSUED_TO, MATCHES_FACE, TRAVELLED_ON, LINKED_TO
    properties_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    @property
    def properties(self):
        try:
            return json.loads(self.properties_json) if self.properties_json else {}
        except Exception:
            return {}

class AuditBlockModel(Base):
    __tablename__ = "audit_blocks"

    block_index = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(String(64), nullable=False)
    event_type = Column(String(64), nullable=False, index=True)
    payload_json = Column(Text, nullable=False)
    prev_hash = Column(String(64), nullable=False)
    block_hash = Column(String(64), nullable=False, unique=True)

class VerificationRecordModel(Base):
    __tablename__ = "verification_records"

    id = Column(String(64), primary_key=True)
    timestamp = Column(String(64), nullable=False)
    document_type = Column(String(32), nullable=True, default="UNKNOWN")
    document_number = Column(String(64), nullable=True, default="NONE")
    holder_name = Column(String(128), nullable=True, default="UNIDENTIFIED")
    nationality = Column(String(8), nullable=True, default="UNKNOWN")
    trust_score = Column(Float, nullable=False)
    trust_chain_broken_layer = Column(String(64), nullable=True)
    fracture_detected = Column(Boolean, default=False)
    second_look_verdict = Column(String(32), default="CLEAR")
    officer_decision = Column(String(32), default="PENDING")
    officer_notes = Column(Text, default="")
    details_json = Column(Text, default="{}")

class OfficerModel(Base):
    __tablename__ = "officers"

    badge_id = Column(String(64), primary_key=True, index=True)
    full_name = Column(String(128), nullable=False)
    password_hash = Column(String(128), nullable=False)
    salt = Column(String(64), nullable=False)
    rank = Column(String(128), nullable=False, default="Border Inspection Officer")
    checkpoint = Column(String(128), nullable=False, default="PANITANKI")
    clearance_level = Column(String(64), nullable=False, default="LEVEL_3_SECURE")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
