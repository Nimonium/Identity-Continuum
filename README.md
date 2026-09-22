# Identity Continuum

<div align="center">

```
  ___ ___  ___ _  _ _____ ___ _____   __   ___ ___  _  _ _____ ___ _  _ _   _ _   _ __  __ 
 |_ _|   \| __| \| |_   _|_ _|_   _\ \ / /  / __/ _ \| \| |_   _|_ _| \| | | | | | |  \/  |
  | || |) | _|| .` | | |  | |  | |  \ V /  | (_| (_) | .` | | |  | || .` | |_| | |_| | |\/| |
 |___|___/|___|_|\_| |_| |___| |_|   |_|    \___\___/|_|\_| |_| |___|_|\_|\___/ \___/|_|  |_|
```

### **Continuous Zero-Trust Border Intelligence Platform**

*Next-generation real-time identity verification engineered with multi-spectral document forensics, neural biometric embeddings, temporal continuity graph engines, and an immutable cryptographic audit ledger.*

<br/>

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.2+-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)](https://pytorch.org)
[![FaceNet](https://img.shields.io/badge/FaceNet-InceptionResnetV1-007ACC?style=for-the-badge&logo=python&logoColor=white)](https://github.com/timesler/facenet-pytorch)
[![EasyOCR](https://img.shields.io/badge/EasyOCR-ICAO_9303-FF6F00?style=for-the-badge&logo=opencv&logoColor=white)](https://github.com/JaidedAI/EasyOCR)
[![WebSocket](https://img.shields.io/badge/WebSocket-Real--Time_Stream-010101?style=for-the-badge&logo=socketdotio&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)
[![SHA-256 Ledger](https://img.shields.io/badge/Ledger-SHA--256_Immutable-4CAF50?style=for-the-badge&logo=blockchaindotcom&logoColor=white)](https://en.wikipedia.org/wiki/SHA-2)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

<br/>

[Key Features](#-key-features) •
[Verification Pipeline](#-the-9-module-zero-trust-pipeline) •
[Portals & UI](#-two-specialized-portals) •
[Architecture](#-system-architecture) •
[Quick Start](#-quick-start) •
[API Reference](#-api--websocket-reference) •
[Security & Compliance](#-security-privacy--cryptography)

</div>

---

## 🧭 Overview

Traditional border inspection points rely on fragmented checkpoints, disconnected databases, and manual document inspection susceptible to sophisticated spoofing, identity theft, and synthetic identity fraud.

**Identity Continuum** introduces a **continuous, multi-layered Zero-Trust verification framework** that unites:
- **Optical Document Intake & Auto-Orientation**: CLAHE enhanced OCR and ICAO 9303 checksum validation for TD1 (National ID) and TD3 (Passport) documents.
- **Micro-Forensics**: Error Level Analysis (ELA) and Fast Fourier Transform (FFT) 2D frequency spectral analysis to detect digital manipulation and copy-paste splices.
- **Deep Biometric Matching**: MTCNN multi-scale landmark localization paired with 512-dimensional FaceNet (`InceptionResnetV1`) cosine distance scoring, resilient to smartphone portrait rotations.
- **Identity Graph & Continuity Engine**: Graph collision detection tracking temporal milestones (flight manifests, visa issuances, past entries) to catch fractured and duplicated identities.
- **Immutable SHA-256 Audit Ledger**: Cryptographically chained blocks guaranteeing tamper-evident auditing for border authorities.

---

## ✨ Key Features

| Capability | Technical Implementation | Impact |
| :--- | :--- | :--- |
| **Biometric Verification** | MTCNN Landmark Detection + FaceNet InceptionResnetV1 | 512-D neural embeddings with cosine similarity matching and auto-alignment. |
| **ICAO 9303 MRZ Engine** | EasyOCR + Auto-Orientation + (7, 3, 1) Check Digit Weights | Cryptographically validates document number, date of birth, expiration, and composite checksums. |
| **Multi-Spectral Forensics** | Error Level Analysis (ELA) + FFT 2D Spectral Ghosting | Identifies re-compression artifacts, cloned photo patches, and modified text fields. |
| **Graph Collision Engine** | Topological Graph Traversal & Conflict Resolution | Flags synthetic identities, split timelines, and biographical attribute discrepancies. |
| **Temporal Continuity** | Event Sequencing & Milestone Integrity Analyzer | Detects impossible travel anomalies, concurrent border crossings, and timeline fractures. |
| **Cryptographic Ledger** | SHA-256 Chained Hash Blocks with Merkle Verification | Provides non-repudiation and court-admissible audit proof of border inspection outcomes. |
| **Real-Time WebSocket** | 9-Stage Event Telemetry with Sub-100ms Latency | Streams stage-by-stage verification progress and diagnostic anomalies directly to the user and officer. |

---

## ⚡ The 9-Module Zero-Trust Pipeline

Every passenger verification executes through an unbroken 9-module chain of trust:

```mermaid
flowchart LR
    A[Doc & Selfie Capture] --> M1[Module 1: Intake & OCR]
    M1 --> M2[Module 2: ICAO Checksum]
    M2 --> M5[Module 5: Forensic ELA/FFT]
    M5 --> M6[Module 6: MTCNN + FaceNet]
    M6 --> M3[Module 3: Identity Graph]
    M3 --> M4[Module 4: Continuity Engine]
    M4 --> M7[Module 7: Zero-Trust Scoring]
    M7 --> M8[Module 8: Decision Engine]
    M8 --> M9[Module 9: SHA-256 Ledger]
    M9 --> Output[Clearance / Officer Review]
```

### Module Breakdown

1. **Module 1: Document Intake & Pre-Processing (`module1_intake.py`)**
   - Applies Contrast Limited Adaptive Histogram Equalization (CLAHE) and auto-detects 0°, 90°, 180°, and 270° orientation flips common in smartphone camera captures.
   - Extracts OCR bounding boxes and isolates the Machine Readable Zone (MRZ).

2. **Module 2: ICAO 9303 MRZ Validation (`module2_validator.py`)**
   - Parses TD1 (3-line, 30-char) and TD3 (2-line, 44-char) standard formats.
   - Validates document number, birth date, expiration date, and personal number check digits using standard ICAO modulus 10 weighting $(7, 3, 1)$.

3. **Module 5: Digital Forensics & Tamper Detection (`module5_forensics.py`)**
   - **Error Level Analysis (ELA)**: Recompresses the document image at 95% quality and evaluates pixel difference matrices to reveal modified regions.
   - **Fast Fourier Transform (FFT)**: Computes 2D power spectral density to locate periodic frequency spikes from cloned elements or synthetic copy-pastes.

4. **Module 6: Neural Biometric Matcher (`module6_face_verifier.py`)**
   - Uses Multi-task Cascaded Convolutional Networks (MTCNN) to isolate and align facial landmarks from both document and live capture.
   - Projects faces into 512-dimensional vector space using FaceNet (`InceptionResnetV1` pretrained on VGGFace2) and calculates cosine similarity confidence score.

5. **Module 3: Identity Graph DNA Engine (`module3_identity_graph.py`)**
   - Maintains an in-memory bi-directional graph connecting biometric clusters, document serials, passport numbers, and traveler profile nodes.
   - Detects **Identity Fractures**: when a single biometrics profile collides with mismatched biographical identities or across contradictory document trees.

6. **Module 4: Identity Continuity Engine (`module4_continuity.py`)**
   - Chronologically orders prior border encounters, travel authorizations, visa issuances, and biometric clearances into an uninterrupted identity timeline.
   - Identifies temporal impossibilities (e.g., crossing two distant international borders within 2 hours).

7. **Module 7: Zero-Trust Evidence Chain Scorer (`module7_trust_engine.py`)**
   - Computes weighted Trust Score ($0 - 100$) across 6 independent threat vectors: document integrity, MRZ checksum, forensic tampering, biometric cosine similarity, graph continuity, and timeline sanity.
   - If any core zero-trust layer fails, an explicit `trust_chain_broken_layer` is signaled.

8. **Module 8: Real-Time Adjudication & Officer Second-Look**
   - Automated clearance granted for records with Trust Score $\ge 80$ and zero fractures.
   - Immediate escalation to secondary inspection console for anomalous scans.

9. **Module 9: Immutable Audit Ledger (`module9_audit_ledger.py`)**
   - Mints a cryptographically signed block with parent hash linkage:
     $$\text{Block Hash} = \text{SHA256}(\text{Index} + \text{PrevHash} + \text{Timestamp} + \text{PayloadHash} + \text{OfficerDecision})$$
   - Full chain auditability prevents tampering, deletion, or backdating.

---

## 🖥️ Two Specialized Portals

The platform ships with two unified single-page applications served directly by FastAPI:

### 1. 🛂 Traveler Self-Service Portal (`http://localhost:8000/`)
- **Interactive Document Intake**: Upload or snap international travel documents (passports, national ID cards).
- **BlazeFace Biometric Capture**: Real-time WebGL biometric alignment oval with auto-capture shutter upon face stabilization.
- **Live Progress Telemetry**: Watch all 9 verification stages execute with instant feedback.
- **Verification History**: Review past clearance records and trust certificates.

### 2. 🛡️ Officer Command & Decision Console (`http://localhost:8000/officer/`)
- **Secure Officer Sign-In**: Role-based checkpoint terminal authentication (PBKDF2-HMAC-SHA256).
- **Forensic Inspection Suite**: Side-by-side document and selfie inspection with ELA tamper heatmaps.
- **Graph & Time Machine Visualizer**: Interactive network graphs highlighting identity collisions and temporal milestones.
- **One-Click Adjudication**: Authorize entry (`CLEARED`), escalate (`SECONDARY REVIEW`), or reject (`DENIED ENTRY`).
- **Ledger Verification**: Instant cryptographic integrity check over the entire immutable audit chain.

---

## 🗂️ System Architecture

```text
Identity Continuum/
├── backend/
│   ├── main.py                      # FastAPI server, WebSocket endpoints & routing
│   ├── auth.py                      # PBKDF2 officer session authentication
│   ├── database.py                  # SQLAlchemy engine & SQLite persistence
│   ├── models.py                    # ORM schema (Verifications, Officers, Ledger)
│   ├── seed_data.py                 # Multi-persona synthetic test dataset
│   ├── modules/                     # Core verification pipeline modules
│   │   ├── module1_intake.py        # CLAHE, auto-orientation, OCR & MRZ crop
│   │   ├── module2_validator.py     # ICAO 9303 checksum & parity calculator
│   │   ├── module3_identity_graph.py# Graph collision & fracture detection
│   │   ├── module4_continuity.py    # Temporal milestone timeline engine
│   │   ├── module5_forensics.py     # ELA & FFT 2D spectral tamper analysis
│   │   ├── module6_face_verifier.py # MTCNN alignment + 512-D FaceNet embeddings
│   │   ├── module7_trust_engine.py  # Multi-vector zero-trust scoring engine
│   │   └── module9_audit_ledger.py  # SHA-256 chained cryptographic ledger
│   ├── scripts/                     # Automated benchmarks and test runners
│   ├── tests/                       # Pytest test suites
│   └── static/                      # Test assets, personas, and screenshots
├── frontend/
│   ├── user/                        # Traveler Portal (HTML5 / Tailwind / Vanilla JS)
│   │   ├── index.html               # Traveler SPA shell
│   │   ├── app.js                   # Client controller & BlazeFace auto-shutter
│   │   └── styles.css               # Design tokens & animations
│   └── officer/                     # Officer Console (HTML5 / Tailwind / Lucide)
│       ├── index.html               # Officer dashboard shell
│       ├── script.js                # Inspection UI, Graph renderer & Ledger auditor
│       └── styles.css               # High-density mission-critical styling
└── README.md                        # Documentation
```

---

## 🚀 Quick Start

### Prerequisites
- **Python**: `3.10` or higher (`3.11` / `3.12` recommended)
- **Node.js**: (Optional, for end-to-end headless testing)
- **Hardware**: CPU supported; CUDA GPU automatically utilized if available for PyTorch.

### 1. Clone the Repository
```bash
git clone https://github.com/Nimonium/Identity-Continuum.git
cd Identity-Continuum
```

### 2. Set Up a Virtual Environment
```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
# Or install core packages directly:
pip install fastapi uvicorn sqlalchemy pydantic facenet-pytorch easyocr opencv-python-headless pillow torch numpy
```

### 4. Run the Platform
```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

- **Traveler Portal**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Officer Inspection Console**: [http://127.0.0.1:8000/officer](http://127.0.0.1:8000/officer)
- **Interactive OpenAPI Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🔑 Demo Officer Credentials

Pre-configured inspection accounts for testing the **Officer Inspection Console**:

| Badge ID | Officer Name | Rank / Station | Default Password | Clearance Level |
| :--- | :--- | :--- | :--- | :--- |
| `OFF-2026` | **Captain R. Verma** | Senior Inspector (DELHI-T3) | `BorderSecure2026!` | `LEVEL_3_SECURE` |
| `SSB-0421` | **M. Chourasiya** | Senior Officer (PANITANKI) | `BorderSecure2026!` | `LEVEL_3_SECURE` |
| `CBP-8819` | **Sarah Jenkins** | Supervisory Agent (JFK-T4) | `BorderSecure2026!` | `LEVEL_3_SECURE` |
| `UKBF-1092` | **David Sterling** | Senior Officer (LHR-T5) | `BorderSecure2026!` | `LEVEL_3_SECURE` |

---

## 📡 API & WebSocket Reference

### HTTP Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/verify` | Submit document image and live selfie for full pipeline evaluation. |
| `GET` | `/api/verifications` | Fetch paginated historical verification clearance events. |
| `GET` | `/api/verifications/{id}` | Retrieve comprehensive forensic breakdown and audit trail for a specific verification. |
| `POST` | `/api/officer/login` | Authenticate an officer credential and issue an encrypted session token. |
| `POST` | `/api/officer/decision` | Record officer adjudication (`CLEARED`, `REFERRED_TO_SECONDARY`, `DENIED_ENTRY`). |
| `GET` | `/api/graph/{person_id}` | Retrieve traveler node relationships and timeline milestones. |
| `GET` | `/api/ledger` | Fetch immutable audit ledger blocks. |
| `GET` | `/api/ledger/verify` | Verify cryptographic SHA-256 chain integrity across all blocks. |
| `GET` | `/health` | Service uptime and neural model readiness status. |

### Real-Time WebSocket Streaming
- **Connection URL**: `ws://127.0.0.1:8000/ws/verify`
- **Protocol**: Send JSON payload containing base64 document and live selfie images:
  ```json
  {
    "document_image": "data:image/jpeg;base64,...",
    "live_image": "data:image/jpeg;base64,...",
    "scenario": "traveler-live"
  }
  ```
- **Events**: Receives incremental module events (`MODULE_1_INTAKE`, `MODULE_2_VALIDATOR`, `MODULE_5_FORENSICS`, `MODULE_6_BIOMETRICS`, `MODULE_3_4_CONTINUITY_GRAPH`, `MODULE_7_TRUST`, `MODULE_9_LEDGER`) with per-step progress percentage and millisecond latencies.

---

## 🔒 Security, Privacy & Cryptography

1. **Ephemeral Biometrics**: Raw biometric face crops and high-resolution captures are processed in memory and never persisted in raw form without explicit compliance policies. Face embeddings are stored as hashed vectors.
2. **Cryptographic Non-Repudiation**: Every decision made by an automated rule or a human officer is cryptographically committed to the audit ledger block with the officer's badge ID and timestamp.
3. **Tamper Detection**: Altering any historical row in the SQLite database breaks the SHA-256 hash pointer of subsequent blocks, causing `/api/ledger/verify` to immediately flag the discrepancy.

---

## 🧪 Testing & Verification

Run the automated regression test suite to validate OCR, ICAO checksum calculations, and biometric matching:

```bash
# Run pytest test suite
pytest backend/tests/ -v

# Run full pipeline regression script
python backend/scripts/run_full_regression.py
```

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

<div align="center">
  <sub>Built with ❤️ for modern, secure, and seamless international border intelligence.</sub>
</div>
