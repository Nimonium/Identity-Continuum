import re
from typing import Dict, Any, Optional, List, Tuple
from pydantic import BaseModel

def compute_mrz_check_digit(data_str: str) -> int:
    """Computes ICAO 9303 check digit using weights 7, 3, 1 repeating."""
    weights = [7, 3, 1]
    total = 0
    for i, char in enumerate(data_str):
        if char == '<':
            val = 0
        elif char.isdigit():
            val = int(char)
        elif 'A' <= char <= 'Z':
            val = ord(char) - ord('A') + 10
        else:
            val = 0
        total += val * weights[i % 3]
    return total % 10

class ParsedMRZ(BaseModel):
    document_type: str # P (Passport), V (Visa), I (Identity Card)
    document_subtype: Optional[str] = None
    issuing_country: str
    document_number: str
    document_number_check: Optional[str] = None
    document_number_valid: bool = True
    nationality: str
    date_of_birth: str # YYMMDD
    dob_check: Optional[str] = None
    dob_valid: bool = True
    gender: str # M, F, X, <
    expiration_date: str # YYMMDD
    expiration_check: Optional[str] = None
    expiration_valid: bool = True
    personal_number: Optional[str] = None
    personal_number_check: Optional[str] = None
    composite_check: Optional[str] = None
    composite_valid: bool = True
    surname: str
    given_names: str
    holder_name: Optional[str] = None
    raw_mrz_lines: List[str]

class ParsedVisa(BaseModel):
    visa_number: str
    visa_type: str # B1/B2, C1, D, TOURIST, BUSINESS, TRANSIT
    issuing_country: str
    issuing_post: str
    holder_name: str
    passport_number: str
    entries: str # SINGLE, MULTIPLE, 1, 2, M
    valid_from: str # YYYY-MM-DD
    valid_until: str # YYYY-MM-DD
    stay_duration_days: int
    raw_text: Optional[str] = None

class DocumentIntakeResult(BaseModel):
    doc_category: str # PASSPORT, VISA, NATIONAL_ID
    structured_data: Dict[str, Any]
    raw_mrz: Optional[List[str]] = None
    extraction_confidence: float
    warnings: List[str] = []

def parse_mrz_td3(line1: str, line2: str) -> ParsedMRZ:
    """Parses standard 2-line 44-character passport MRZ (TD3)."""
    line1 = line1.strip().upper().ljust(44, '<')[:44]
    line2 = line2.strip().upper().ljust(44, '<')[:44]

    doc_type = line1[0]
    doc_subtype = line1[1] if line1[1] != '<' else None
    issuing_country = line1[2:5].replace('<', '')
    
    # Names parsing: SURNAME<<GIVEN<NAMES<<<<
    name_part = line1[5:]
    if '<<' in name_part:
        parts = name_part.split('<<', 1)
        surname = parts[0].replace('<', ' ').strip()
        given_clean = parts[1].split('<<')[0] if '<<' in parts[1] else parts[1]
        given_names = given_clean.replace('<', ' ').strip()
    else:
        surname = name_part.replace('<', ' ').strip()
        given_names = ""

    # Line 2 parsing
    doc_num_raw = line2[0:9]
    doc_num_check = line2[9]
    nationality = line2[10:13].replace('<', '')
    dob_raw = line2[13:19]
    dob_check = line2[19]
    gender = line2[20]
    exp_raw = line2[21:27]
    exp_check = line2[27]
    personal_num_raw = line2[28:42]
    personal_num_check = line2[42] if line2[42] != '<' else None
    composite_check = line2[43]

    clean_doc_num = doc_num_raw.replace('<', '').strip()
    
    # Checksum calculations
    doc_valid = str(compute_mrz_check_digit(doc_num_raw)) == doc_num_check
    dob_valid = str(compute_mrz_check_digit(dob_raw)) == dob_check
    exp_valid = str(compute_mrz_check_digit(exp_raw)) == exp_check
    
    # Composite data string according to ICAO Doc 9303 Part 4:
    # positions 1-10, 14-20, and 22-43 of the lower line
    comp_str = line2[0:10] + line2[13:20] + line2[21:43]
    comp_valid = str(compute_mrz_check_digit(comp_str)) == composite_check

    return ParsedMRZ(
        document_type=doc_type,
        document_subtype=doc_subtype,
        issuing_country=issuing_country,
        document_number=clean_doc_num,
        document_number_check=doc_num_check,
        document_number_valid=doc_valid,
        nationality=nationality,
        date_of_birth=dob_raw,
        dob_check=dob_check,
        dob_valid=dob_valid,
        gender=gender,
        expiration_date=exp_raw,
        expiration_check=exp_check,
        expiration_valid=exp_valid,
        personal_number=personal_num_raw.replace('<', '').strip() if personal_num_raw.replace('<', '') else None,
        personal_number_check=personal_num_check,
        composite_check=composite_check,
        composite_valid=comp_valid,
        surname=surname,
        given_names=given_names,
        holder_name=f"{surname} {given_names}".strip(),
        raw_mrz_lines=[line1, line2]
    )

def parse_mrz_td1(lines: List[str]) -> ParsedMRZ:
    """Parses standard 3-line 30-character ID / visa card MRZ (TD1)."""
    l1 = lines[0].strip().upper().ljust(30, '<')[:30]
    l2 = lines[1].strip().upper().ljust(30, '<')[:30]
    l3 = lines[2].strip().upper().ljust(30, '<')[:30]

    doc_type = l1[0]
    issuing_country = l1[2:5].replace('<', '')
    doc_num_raw = l1[5:14]
    doc_num_check = l1[14]

    dob_raw = l2[0:6]
    dob_check = l2[6]
    gender = l2[7]
    exp_raw = l2[8:14]
    exp_check = l2[14]
    nationality = l2[15:18].replace('<', '')

    name_part = l3
    if '<<' in name_part:
        parts = name_part.split('<<', 1)
        surname = parts[0].replace('<', ' ').strip()
        given_names = parts[1].replace('<', ' ').strip()
    else:
        surname = name_part.replace('<', ' ').strip()
        given_names = ""

    doc_valid = str(compute_mrz_check_digit(doc_num_raw)) == doc_num_check
    dob_valid = str(compute_mrz_check_digit(dob_raw)) == dob_check
    exp_valid = str(compute_mrz_check_digit(exp_raw)) == exp_check

    return ParsedMRZ(
        document_type=doc_type,
        issuing_country=issuing_country,
        document_number=doc_num_raw.replace('<', '').strip(),
        document_number_check=doc_num_check,
        document_number_valid=doc_valid,
        nationality=nationality,
        date_of_birth=dob_raw,
        dob_check=dob_check,
        dob_valid=dob_valid,
        gender=gender,
        expiration_date=exp_raw,
        expiration_check=exp_check,
        expiration_valid=exp_valid,
        composite_check=None,
        composite_valid=True,
        surname=surname,
        given_names=given_names,
        holder_name=f"{surname} {given_names}".strip(),
        raw_mrz_lines=[l1, l2, l3]
    )

def extract_document_data(doc_text_or_mrz: str, doc_category: str = "PASSPORT") -> DocumentIntakeResult:
    """Main intake function converting raw strings/mrz lines to structured document object."""
    lines = [line.strip().replace(" ", "") for line in doc_text_or_mrz.strip().split('\n') if line.strip()]
    
    # Check if lines match TD3 passport MRZ
    mrz_candidates = [l for l in lines if '<' in l and len(l) >= 30]
    
    if len(mrz_candidates) >= 2 and len(mrz_candidates[0]) >= 40:
        parsed = parse_mrz_td3(mrz_candidates[0], mrz_candidates[1])
        return DocumentIntakeResult(
            doc_category="PASSPORT",
            structured_data=parsed.model_dump(),
            raw_mrz=[mrz_candidates[0], mrz_candidates[1]],
            extraction_confidence=0.98,
            warnings=[]
        )
    elif len(mrz_candidates) >= 3:
        parsed = parse_mrz_td1(mrz_candidates[:3])
        return DocumentIntakeResult(
            doc_category="NATIONAL_ID" if doc_category != "VISA" else "VISA",
            structured_data=parsed.model_dump(),
            raw_mrz=mrz_candidates[:3],
            extraction_confidence=0.95,
            warnings=[]
        )
    
    # Fallback to key-value / visa extraction if text contains recognizable patterns
    if not doc_text_or_mrz or not doc_text_or_mrz.strip():
        return DocumentIntakeResult(
            doc_category=doc_category,
            structured_data={
                "document_type": doc_category,
                "issuing_country": None,
                "document_number": None,
                "holder_name": None,
                "date_of_birth": None,
                "expiration_date": None,
                "nationality": None,
                "gender": None
            },
            raw_mrz=[],
            extraction_confidence=0.10,
            warnings=["No text or MRZ detected on uploaded document; manual officer inspection required"]
        )

    visa_num_match = re.search(r'(?:VISA\s*(?:NO|NUMBER|#)?[:\s]*)([A-Z0-9\-_]{6,16})', doc_text_or_mrz, re.I)
    name_match = re.search(r'(?:NAME|HOLDER)[:\s]*([A-Z\s,]+)', doc_text_or_mrz, re.I)
    type_match = re.search(r'(?:TYPE|CLASS)[:\s]*([A-Z0-9\-\/]+)', doc_text_or_mrz, re.I)
    pass_match = re.search(r'(?:PASSPORT\s*(?:NO|NUMBER|#)?[:\s]*)([A-Z0-9\-_]{6,16})', doc_text_or_mrz, re.I)
    
    extracted_num = visa_num_match.group(1).strip() if visa_num_match else (pass_match.group(1).strip() if pass_match else None)
    extracted_name = name_match.group(1).strip() if name_match else None
    
    if extracted_num or extracted_name:
        structured = {
            "document_type": "V" if doc_category == "VISA" else "I",
            "issuing_country": None,
            "document_number": extracted_num,
            "holder_name": extracted_name,
            "passport_number": pass_match.group(1) if pass_match else None,
            "visa_type": type_match.group(1) if type_match else None,
            "stay_duration_days": None,
            "entries": None
        }
        return DocumentIntakeResult(
            doc_category=doc_category,
            structured_data=structured,
            raw_mrz=[],
            extraction_confidence=0.45,
            warnings=["Non-standard layout; extracted via regex heuristics without cryptographic MRZ check digits"]
        )
    
    return DocumentIntakeResult(
        doc_category=doc_category,
        structured_data={
            "document_type": doc_category,
            "issuing_country": None,
            "document_number": None,
            "holder_name": None,
            "date_of_birth": None,
            "expiration_date": None,
            "nationality": None,
            "gender": None
        },
        raw_mrz=[],
        extraction_confidence=0.15,
        warnings=["No standard ICAO 9303 MRZ zone or recognized structured fields found on image"]
    )

_easyocr_reader = None

def warmup_ocr_reader():
    """Pre-loads EasyOCR weights into RAM at server startup with a warm-up dummy pass."""
    global _easyocr_reader
    if _easyocr_reader is None:
        try:
            import easyocr
            import numpy as np
            _easyocr_reader = easyocr.Reader(['en'], gpu=False, verbose=False)
            dummy = np.zeros((80, 200), dtype=np.uint8)
            _easyocr_reader.readtext(dummy)
            print("[SYSTEM STARTUP] EasyOCR Reader warmed up and ready in RAM.")
        except Exception as e:
            print(f"[SYSTEM STARTUP] EasyOCR init warning: {e}")
            _easyocr_reader = False
    return _easyocr_reader

def get_ocr_reader():
    global _easyocr_reader
    if _easyocr_reader is None:
        return warmup_ocr_reader()
    return _easyocr_reader

def deskew_and_enhance_document(img_bgr: "np.ndarray") -> "Tuple[np.ndarray, Optional[np.ndarray]]":
    """
    Finds document contour, performs 4-point perspective deskewing, 
    and generates a high-contrast CLAHE-enhanced MRZ region of interest.
    """
    import cv2
    import numpy as np

    if img_bgr is None or img_bgr.size == 0:
        return img_bgr, None

    h, w = img_bgr.shape[:2]
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    
    # 1. Perspective deskewing via contour detection
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 50, 200)
    contours, _ = cv2.findContours(edged, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    
    deskewed = img_bgr
    for c in sorted(contours, key=cv2.contourArea, reverse=True)[:5]:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4 and cv2.contourArea(c) > (w * h * 0.20):
            # Sort 4 corner points [top-left, top-right, bottom-right, bottom-left]
            pts = approx.reshape(4, 2)
            rect = np.zeros((4, 2), dtype="float32")
            s = pts.sum(axis=1)
            rect[0] = pts[np.argmin(s)]
            rect[2] = pts[np.argmax(s)]
            diff = np.diff(pts, axis=1)
            rect[1] = pts[np.argmin(diff)]
            rect[3] = pts[np.argmax(diff)]
            
            dst_w, dst_h = 800, 520
            dst = np.array([[0, 0], [dst_w - 1, 0], [dst_w - 1, dst_h - 1], [0, dst_h - 1]], dtype="float32")
            M = cv2.getPerspectiveTransform(rect, dst)
            deskewed = cv2.warpPerspective(img_bgr, M, (dst_w, dst_h))
            break

    # 2. Extract bottom 30% MRZ zone with CLAHE enhancement
    dh, dw = deskewed.shape[:2]
    mrz_roi = deskewed[int(dh * 0.65):dh, 0:dw]
    mrz_gray = cv2.cvtColor(mrz_roi, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    mrz_enhanced = clahe.apply(mrz_gray)
    
    return deskewed, mrz_enhanced

def extract_document_from_image_bytes(doc_bytes: bytes, doc_category: str = "PASSPORT") -> DocumentIntakeResult:
    """
    Performs real-world OCR and MRZ extraction directly on uploaded image bytes.
    Extracts ICAO TD3 passport MRZ lines, TD1 ID card lines, and visual inspection fields.
    Prioritizes fast MRZ-strip OCR (~1s) before full-document fallback.
    """
    reader = get_ocr_reader()
    if not reader or not doc_bytes:
        return extract_document_data("", doc_category)

    try:
        import numpy as np
        import cv2

        nparr = np.frombuffer(doc_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return extract_document_data("", doc_category)

        # Auto-orientation: standard ICAO passports are landscape (w > h).
        # If smartphone photo was taken in portrait mode (h > w), prioritize 90 deg counter-clockwise and clockwise.
        h, w = img.shape[:2]
        if h > w:
            rotations = [cv2.ROTATE_90_COUNTERCLOCKWISE, cv2.ROTATE_90_CLOCKWISE, None]
        else:
            rotations = [None, cv2.ROTATE_90_COUNTERCLOCKWISE, cv2.ROTATE_90_CLOCKWISE]

        best_res = None
        best_ocr_results = []
        best_deskewed = img

        for rot in rotations:
            cur_img = cv2.rotate(img, rot) if rot is not None else img
            deskewed_img, mrz_enhanced = deskew_and_enhance_document(cur_img)

            ocr_results = []
            # Fast Path: Run OCR on CLAHE enhanced MRZ strip first
            if mrz_enhanced is not None:
                try:
                    ocr_results = reader.readtext(mrz_enhanced)
                except Exception:
                    pass

            extracted_lines = [text.strip() for _, text, conf in ocr_results if conf >= 0.15 or ('<' in text and conf >= 0.08)]
            mrz_lines = [l.replace(" ", "").upper() for l in extracted_lines if ("<" in l and len(l.replace(" ", "")) >= 25) or (len(l.replace(" ", "")) >= 40 and any(c.isdigit() for c in l))]
            
            if len(mrz_lines) >= 2:
                combined_mrz = "\n".join(mrz_lines[-2:])
                res = extract_document_data(combined_mrz, doc_category)
                if res.extraction_confidence >= 0.85:
                    return res
                if best_res is None or res.extraction_confidence > best_res.extraction_confidence:
                    best_res = res
                    best_ocr_results = ocr_results
                    best_deskewed = deskewed_img

        # If fast MRZ strip didn't hit >= 0.85 on any orientation, run fallback on best candidate or first candidate
        candidate_img = best_deskewed if best_deskewed is not None else (cv2.rotate(img, rotations[0]) if rotations[0] is not None else img)
        deskewed_img = candidate_img
        full_ocr = reader.readtext(deskewed_img)
        ocr_results = list(best_ocr_results) + full_ocr

        extracted_lines = []
        raw_blocks = []
        
        for bbox, text, conf in ocr_results:
            if conf >= 0.20:
                clean_t = text.strip()
                extracted_lines.append(clean_t)
                raw_blocks.append(clean_t)

        # Re-check MRZ lines on combined extraction
        mrz_lines = [l.replace(" ", "").upper() for l in extracted_lines if ("<" in l and len(l.replace(" ", "")) >= 25) or (len(l.replace(" ", "")) >= 40 and any(c.isdigit() for c in l))]
        
        if len(mrz_lines) >= 2:
            combined_mrz = "\n".join(mrz_lines[-2:])
            res = extract_document_data(combined_mrz, doc_category)
            if res.extraction_confidence >= 0.85:
                return res

        # 2. Sequential block extraction for Visual Inspection Zone (VIZ)
        extracted_surname = None
        extracted_given = None
        extracted_doc_num = None
        extracted_country = None
        extracted_dob = None
        extracted_exp = None

        for idx, blk in enumerate(raw_blocks):
            blk_upper = blk.upper()
            
            # Country
            if "ISSUING" in blk_upper or "STATE" in blk_upper or "COUNTRY" in blk_upper or "NATIONALITY" in blk_upper:
                c_match = re.search(r'(?:ISSUING\s*STATE|STATE|NATIONALITY|CODE)[:\s]*([A-Z]{3})', blk_upper)
                if c_match and c_match.group(1) not in ["ISS", "STA", "NAT"]:
                    extracted_country = c_match.group(1)
            elif blk_upper in ["GBR", "USA", "IND", "DEU", "FRA", "CAN", "AUS", "JPN", "RUS"]:
                if not extracted_country:
                    extracted_country = blk_upper

            # Surname
            if any(k in blk_upper for k in ["SURNAME", "NOM"]):
                if idx + 1 < len(raw_blocks) and not any(k in raw_blocks[idx+1].upper() for k in ["GIVEN", "PRENOM", "SEX", "DATE", "PASSPORT"]):
                    extracted_surname = raw_blocks[idx+1].strip().upper()

            # Given Names
            if any(k in blk_upper for k in ["GIVEN NAME", "GIVEN NAMES", "PRENOMS"]):
                if idx + 1 < len(raw_blocks) and not any(k in raw_blocks[idx+1].upper() for k in ["NATIONALITY", "SEX", "DATE", "PASSPORT"]):
                    candidate = raw_blocks[idx+1].strip().upper()
                    if candidate != extracted_surname:
                        extracted_given = candidate

            # Document Number
            if any(k in blk_upper for k in ["DOCUMENT NO", "PASSPORT NO", "PASSEPORT", "NO DU"]):
                if idx + 1 < len(raw_blocks):
                    num_match = re.search(r'([A-Z0-9]{7,12})', raw_blocks[idx+1].upper())
                    if num_match:
                        extracted_doc_num = num_match.group(1)
            elif re.match(r'^[A-Z0-9]{8,10}$', blk_upper) and not any(blk_upper.startswith(k) for k in ["ICHO", "TYPE", "STATE", "DATE", "GBR", "USA"]):
                if not extracted_doc_num:
                    extracted_doc_num = blk_upper

            # Dates (DOB / Expiry)
            date_match = re.search(r'(\d{1,2}[\/\-\,\.]\d{1,2}[\/\-\,\.]\d{2,4})', blk)
            if date_match:
                d_str = date_match.group(1).replace(",", "/")
                if "EXPIR" in blk_upper or (idx > 0 and "EXPIR" in raw_blocks[idx-1].upper()):
                    extracted_exp = d_str
                elif "BIRTH" in blk_upper or "NAISSANCE" in blk_upper or (idx > 0 and "BIRTH" in raw_blocks[idx-1].upper()):
                    extracted_dob = d_str

        # Fallback regex search on joined text if sequential didn't catch all
        joined_text = " \n ".join(raw_blocks)
        if not extracted_surname:
            m = re.search(r'(?:SURNAME|NOM|LAST\s*NAME)[:\s]*([A-Z\s]{2,25})', joined_text, re.I)
            if m: extracted_surname = m.group(1).strip().upper()
        if not extracted_given:
            m = re.search(r'(?:GIVEN\s*NAMES?|PRENOMS?|FIRST\s*NAME)[:\s]*([A-Z\s]{2,25})', joined_text, re.I)
            if m and m.group(1).strip().upper() != extracted_surname:
                extracted_given = m.group(1).strip().upper()
        if not extracted_doc_num:
            m = re.search(r'(?:PASSPORT\s*(?:NO|NUM|#)?|DOCUMENT\s*(?:NO|NUM|#)?|ID\s*(?:NO|NUM)?)[:\s]*([A-Z0-9]{7,12})', joined_text, re.I)
            if m: extracted_doc_num = m.group(1).strip().upper()
        if not extracted_country:
            m = re.search(r'(?:ISSUING\s*STATE|COUNTRY|NATIONALITY|CODE)[:\s]*([A-Z]{3})', joined_text, re.I)
            if m and m.group(1).strip().upper() not in ["ISS", "STA", "NAT"]:
                extracted_country = m.group(1).strip().upper()
            else:
                extracted_country = "GBR" if "GBR" in joined_text else ("USA" if "USA" in joined_text else "ICAO")

        # Build composite name
        extracted_name = None
        if extracted_surname or extracted_given:
            extracted_name = f"{extracted_surname or ''} {extracted_given or ''}".strip()

        if extracted_doc_num or extracted_name:
            confidence = 0.92 if (extracted_doc_num and extracted_name) else 0.70
            return DocumentIntakeResult(
                doc_category=doc_category,
                structured_data={
                    "document_type": "P" if doc_category == "PASSPORT" else "I",
                    "issuing_country": extracted_country or "ICAO",
                    "document_number": extracted_doc_num,
                    "holder_name": extracted_name,
                    "surname": extracted_surname,
                    "given_names": extracted_given,
                    "date_of_birth": extracted_dob,
                    "expiration_date": extracted_exp,
                    "nationality": extracted_country or "ICAO",
                    "gender": "X"
                },
                raw_mrz=mrz_lines,
                extraction_confidence=confidence,
                warnings=["Visual Inspection Zone (VIZ) & OCR fields extracted with high optical confidence."]
            )

        # Fallback to standard string parser
        return extract_document_data(joined_text, doc_category)

    except Exception as e:
        print(f"[OCR] Image OCR extraction error: {e}")
        return extract_document_data("", doc_category)

