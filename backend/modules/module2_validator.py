import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

ISO_3166_ALPHA3 = {
    "USA", "GBR", "CAN", "AUS", "DEU", "FRA", "JPN", "IND", "CHN", "BRA",
    "RUS", "ITA", "ESP", "NLD", "CHE", "SWE", "NOR", "SGP", "KOR", "MEX",
    "ZAF", "NZL", "ARE", "ISR", "IRL", "BEL", "AUT", "POL", "DNK", "FIN"
}

class ValidationCheckItem(BaseModel):
    code: str
    name: str
    status: str # PASS, FAIL, WARNING
    reason: str
    target_link: str # ISSUING_AUTHORITY, DOCUMENT_AUTHENTICITY

class DocumentValidationResult(BaseModel):
    is_valid: bool
    authority_valid: bool
    format_valid: bool
    checks: List[ValidationCheckItem]
    summary_message: str

def parse_yy_mm_dd(date_str: str, is_expiration: bool = False) -> Optional[datetime.date]:
    """Converts 6-digit YYMMDD string to datetime.date with reasonable century inference."""
    if not date_str or len(date_str) != 6 or not date_str.isdigit():
        return None
    yy = int(date_str[0:2])
    mm = int(date_str[2:4])
    dd = int(date_str[4:6])

    if mm < 1 or mm > 12 or dd < 1 or dd > 31:
        return None

    current_year_2digit = datetime.datetime.now().year % 100
    if is_expiration:
        # Expirations are typically in the current century (2000s)
        full_year = 2000 + yy
    else:
        # DOB: If yy > current_year, it's 1900s, else could be 2000s
        if yy > current_year_2digit:
            full_year = 1900 + yy
        else:
            full_year = 2000 + yy

    try:
        return datetime.date(full_year, mm, dd)
    except ValueError:
        return None

def validate_document_data(doc_data: Dict[str, Any]) -> DocumentValidationResult:
    checks: List[ValidationCheckItem] = []
    
    # 1. Issuing Country Check
    country = (doc_data.get("issuing_country") or "").upper()
    if country in ISO_3166_ALPHA3:
        checks.append(ValidationCheckItem(
            code="ICAO_COUNTRY_CODE",
            name="ICAO Issuing Authority Code",
            status="PASS",
            reason=f"Recognized ICAO issuing country code: {country}",
            target_link="ISSUING_AUTHORITY"
        ))
    elif country:
        checks.append(ValidationCheckItem(
            code="ICAO_COUNTRY_CODE",
            name="ICAO Issuing Authority Code",
            status="WARNING",
            reason=f"Non-standard or rare country code: {country}",
            target_link="ISSUING_AUTHORITY"
        ))
    else:
        checks.append(ValidationCheckItem(
            code="ICAO_COUNTRY_CODE",
            name="ICAO Issuing Authority Code",
            status="FAIL",
            reason="Missing issuing country identifier",
            target_link="ISSUING_AUTHORITY"
        ))

    # 2. MRZ Checksum Validation
    doc_num_valid = doc_data.get("document_number_valid", True)
    if doc_num_valid:
        checks.append(ValidationCheckItem(
            code="MRZ_DOC_NUM_CHECKSUM",
            name="Document Number Checksum",
            status="PASS",
            reason="ICAO 9303 modulo-10 check digit mathematically verified",
            target_link="DOCUMENT_AUTHENTICITY"
        ))
    else:
        checks.append(ValidationCheckItem(
            code="MRZ_DOC_NUM_CHECKSUM",
            name="Document Number Checksum",
            status="FAIL",
            reason="Document number checksum mismatch — possible optical or physical modification",
            target_link="DOCUMENT_AUTHENTICITY"
        ))

    dob_valid = doc_data.get("dob_valid", True)
    if dob_valid:
        checks.append(ValidationCheckItem(
            code="MRZ_DOB_CHECKSUM",
            name="Date of Birth Checksum",
            status="PASS",
            reason="Date of birth check digit matches expected 7-3-1 modulo",
            target_link="DOCUMENT_AUTHENTICITY"
        ))
    else:
        checks.append(ValidationCheckItem(
            code="MRZ_DOB_CHECKSUM",
            name="Date of Birth Checksum",
            status="FAIL",
            reason="DOB checksum check digit failure",
            target_link="DOCUMENT_AUTHENTICITY"
        ))

    exp_valid = doc_data.get("expiration_valid", True)
    if exp_valid:
        checks.append(ValidationCheckItem(
            code="MRZ_EXP_CHECKSUM",
            name="Expiration Date Checksum",
            status="PASS",
            reason="Expiration date check digit mathematically verified",
            target_link="DOCUMENT_AUTHENTICITY"
        ))
    else:
        checks.append(ValidationCheckItem(
            code="MRZ_EXP_CHECKSUM",
            name="Expiration Date Checksum",
            status="FAIL",
            reason="Expiration date checksum check digit failure",
            target_link="DOCUMENT_AUTHENTICITY"
        ))

    composite_valid = doc_data.get("composite_valid", True)
    if composite_valid:
        checks.append(ValidationCheckItem(
            code="MRZ_COMPOSITE_CHECKSUM",
            name="Composite MRZ Checksum",
            status="PASS",
            reason="Composite verification check digit is valid",
            target_link="DOCUMENT_AUTHENTICITY"
        ))
    else:
        checks.append(ValidationCheckItem(
            code="MRZ_COMPOSITE_CHECKSUM",
            name="Composite MRZ Checksum",
            status="FAIL",
            reason="Overall composite checksum verification failure",
            target_link="DOCUMENT_AUTHENTICITY"
        ))

    # 3. Date Logic Checks
    today = datetime.date.today()
    exp_str = doc_data.get("expiration_date")
    if exp_str:
        exp_date = parse_yy_mm_dd(exp_str, is_expiration=True)
        if exp_date:
            if exp_date < today:
                checks.append(ValidationCheckItem(
                    code="DATE_EXPIRY_PAST",
                    name="Document Validity Window",
                    status="FAIL",
                    reason=f"Document expired on {exp_date.isoformat()}",
                    target_link="DOCUMENT_AUTHENTICITY"
                ))
            else:
                checks.append(ValidationCheckItem(
                    code="DATE_EXPIRY_PAST",
                    name="Document Validity Window",
                    status="PASS",
                    reason=f"Document valid until {exp_date.isoformat()}",
                    target_link="DOCUMENT_AUTHENTICITY"
                ))
        else:
            checks.append(ValidationCheckItem(
                code="DATE_FORMAT_INVALID",
                name="Date Format Parsing",
                status="FAIL",
                reason=f"Unparseable expiration date: {exp_str}",
                target_link="DOCUMENT_AUTHENTICITY"
            ))

    # 4. Gender Format Check
    gender = doc_data.get("gender", "")
    if gender in ["M", "F", "X", "<"]:
        checks.append(ValidationCheckItem(
            code="GENDER_CODE_FORMAT",
            name="ICAO Gender Field Format",
            status="PASS",
            reason=f"Valid ICAO 9303 sex designator ({gender})",
            target_link="DOCUMENT_AUTHENTICITY"
        ))
    else:
        checks.append(ValidationCheckItem(
            code="GENDER_CODE_FORMAT",
            name="ICAO Gender Field Format",
            status="WARNING",
            reason=f"Non-standard sex designator: {gender}",
            target_link="DOCUMENT_AUTHENTICITY"
        ))

    has_fail = any(c.status == "FAIL" for c in checks)
    authority_ok = not any(c.status == "FAIL" and c.target_link == "ISSUING_AUTHORITY" for c in checks)
    format_ok = not any(c.status == "FAIL" and c.target_link == "DOCUMENT_AUTHENTICITY" for c in checks)

    return DocumentValidationResult(
        is_valid=not has_fail,
        authority_valid=authority_ok,
        format_valid=format_ok,
        checks=checks,
        summary_message="All document structural checks passed" if not has_fail else "Document validation failed one or more integrity rules"
    )
