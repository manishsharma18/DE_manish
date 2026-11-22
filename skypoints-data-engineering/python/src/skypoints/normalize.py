
from datetime import date, datetime
import re
import pandas as pd

ALIASES = {
    "id": "member_id", "unique id": "member_id",
    "name": "member_name", "member name": "member_name",
    "dob": "date_of_birth", "date of birth": "date_of_birth",
    "tiercode": "tier_code", "tier type": "tier_code",
    "enrollmentdate": "enrollment_date", "date of enrollment": "enrollment_date",
    "individual or corporate": "member_type",
    "flight date": "last_flight_date", "flightdate": "last_flight_date",
    "date of flight": "last_flight_date",
    "agent_name": "agent_name", "state": "state", "country": "country",
    "post code": "post_code", "postcode": "post_code",
    "is_active": "is_active", "active member": "is_active",
}

def canonical_column(name: str) -> str:
    key = re.sub(r"\s+", " ", str(name).strip()).lower()
    return ALIASES.get(key, key.replace(" ", "_"))

def parse_source_date(value):
    """Parse ISO, YYYYMMDD, and the supplied USA workbook's MDDYYYY/MMDDYYYY values."""
    if pd.isna(value) or value == "":
        return None
    if isinstance(value, (pd.Timestamp, datetime, date)):
        return pd.Timestamp(value).date()
    if isinstance(value, (int, float)):
        if not float(value).is_integer():
            return None
        value = str(int(value))
    raw = str(value).strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw):
        try:
            return date.fromisoformat(raw)
        except ValueError:
            return None
    if re.fullmatch(r"\d{8}", raw):
        for fmt in ("%Y%m%d", "%m%d%Y"):
            try:
                return datetime.strptime(raw, fmt).date()
            except ValueError:
                pass
        return None
    if re.fullmatch(r"\d{7}", raw):
        try:
            return datetime.strptime("0" + raw, "%m%d%Y").date()
        except ValueError:
            return None
    return None

def normalize_frame(df: pd.DataFrame, country: str, source_file: str, as_of=None):
    from datetime import date as date_cls
    as_of = as_of or date_cls.today()
    out = df.copy()
    out.columns = [canonical_column(c) for c in out.columns]

    for col in ["member_id", "member_name", "date_of_birth", "tier_code",
                "enrollment_date", "member_type", "last_flight_date",
                "agent_name", "state", "country", "post_code", "is_active"]:
        if col not in out.columns:
            out[col] = None

    # Country in these sample workbooks is represented by the workbook itself.
    out["country"] = out["country"].where(out["country"].notna(), country)
    out["source_country"] = country
    out["source_file"] = source_file
    out["member_id"] = out["member_id"].astype("string").str.strip()
    out["member_name"] = out["member_name"].astype("string").str.strip()
    out["tier_code"] = out["tier_code"].astype("string").str.strip().str.upper()
    out["date_of_birth"] = out["date_of_birth"].map(parse_source_date)
    out["enrollment_date"] = out["enrollment_date"].map(parse_source_date)
    out["last_flight_date"] = out["last_flight_date"].map(parse_source_date)

    def age(dob):
        if dob is None or pd.isna(dob):
            return None
        return as_of.year - dob.year - ((as_of.month, as_of.day) < (dob.month, dob.day))

    out["age"] = out["date_of_birth"].map(age)
    out["stale_member"] = out["last_flight_date"].map(
        lambda d: None if d is None or pd.isna(d) else (as_of - d).days > 90
    )
    return out
