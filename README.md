# Identity Continuum

**Continuous Zero-Trust Border Intelligence Platform**

A real-time identity verification system powered by MTCNN + FaceNet biometric matching, ICAO 9303 MRZ extraction, ELA/FFT document forensics, and an immutable SHA-256 audit ledger.

## Architecture

```
Identity Continuum/
├── backend/                    # FastAPI Python backend
│   ├── main.py                 # Core API server & verification pipeline
│   ├── auth.py                 # Officer authentication (JWT)
│   ├── database.py             # SQLAlchemy database config
│   ├── models.py               # ORM models
│   ├── seed_data.py            # Demo scenario data seeding
│   ├── modules/                # Verification engine modules
│   │   ├── module1_intake.py   # Document OCR & MRZ extraction (EasyOCR)
│   │   ├── module2_validator.py# ICAO 9303 checksum validation
│   │   ├── module3_graph.py    # Identity graph & fracture detection
│   │   ├── module4_continuity.py # Identity continuity timeline
│   │   ├── module5_forensics.py# ELA / FFT tampering detection
│   │   ├── module6_face_verifier.py # MTCNN + FaceNet biometric matching
│   │   ├── module7_trust.py    # Zero-trust evidence chain scoring
│   │   └── module9_ledger.py   # Immutable SHA-256 audit ledger
│   ├── scripts/                # Benchmarking & regression test scripts
│   ├── tests/                  # Pytest test suite
│   └── static/                 # Static assets (demo documents, faces)
├── frontend/
│   ├── user/                   # Traveler verification portal (SPA)
│   └── officer/                # Officer inspection console (SPA)
├── officer dashboard/          # Officer review dashboard
└── user dashboard/             # User-facing dashboard
```

## Key Features

- **9-Module Verification Pipeline**: Document intake → validation → forensics → biometrics → graph analysis → continuity → trust scoring → AI second-look → audit ledger
- **Real MTCNN + FaceNet**: Genuine PyTorch InceptionResnetV1 512-D embeddings with multi-orientation face detection (handles phone-captured portrait passport photos)
- **ICAO 9303 MRZ Parsing**: Full TD3 passport and TD1 ID card MRZ extraction with cryptographic check digit verification
- **Auto-Orientation OCR**: Automatically rotates sideways smartphone passport photos for accurate MRZ reading
- **ELA & FFT Forensics**: Error Level Analysis and Fast Fourier Transform spectral ghost detection for tamper analysis
- **Identity Graph DNA**: Neo4j-style graph collision detection for identity fracture/duplication
- **Immutable Audit Ledger**: SHA-256 chained blocks with Merkle-style integrity verification
- **Officer Decision Console**: JWT-authenticated officer review with approve/deny/escalate workflows

## Quick Start

### Prerequisites
- Python 3.10+
- PyTorch 2.2+
- facenet-pytorch, easyocr, opencv-python, fastapi, uvicorn

### Install & Run

```bash
pip install fastapi uvicorn sqlalchemy pydantic facenet-pytorch easyocr opencv-python-headless pillow torch numpy
cd "Identity Continuum"
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

Open **http://127.0.0.1:8000** in your browser.

### API Documentation
Swagger UI: **http://127.0.0.1:8000/docs**

## Verification Pipeline

| Module | Function | Technology |
|--------|----------|------------|
| Module 1 | Document Intake & OCR | EasyOCR + CLAHE + Auto-Orientation |
| Module 2 | ICAO Validation | MRZ Check Digits (TD1/TD3) |
| Module 3 | Identity Graph DNA | Graph Traversal & Fracture Detection |
| Module 4 | Continuity Engine | Temporal Timeline Analysis |
| Module 5 | Forensics | ELA, FFT Spectral, Metadata Analysis |
| Module 6 | Biometrics | MTCNN + FaceNet InceptionResnetV1 |
| Module 7 | Zero-Trust Scoring | Multi-layer Evidence Chain |
| Module 9 | Audit Ledger | SHA-256 Immutable Chain |

## License

MIT
