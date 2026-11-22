
from datetime import date
import pandas as pd
from python.src.skypoints.normalize import parse_source_date, normalize_frame
from python.src.skypoints.validate import validate_members

def test_parse_iso_and_assessment_date():
    assert parse_source_date("2022-03-12") == date(2022, 3, 12)
    assert parse_source_date("20101012") == date(2010, 10, 12)
    assert parse_source_date(6152022) == date(2022, 6, 15)
    assert parse_source_date(1052022) == date(2022, 1, 5)
    assert parse_source_date("2021-13-13") is None

def test_missing_optional_dob_is_allowed():
    df = pd.DataFrame([{
        "ID": "22", "Name": "Test Member", "TierCode": "GLD",
        "EnrollmentDate": "20220101", "FlightDate": None
    }])
    normalized = normalize_frame(df, "USA", "USA.xlsx", as_of=date(2024, 1, 1))
    accepted, rejected = validate_members(normalized)
    assert len(accepted) == 1
    assert len(rejected) == 0
    assert accepted.iloc[0]["age"] is None

def test_missing_mandatory_member_name_rejected():
    df = pd.DataFrame([{
        "member_id": "22", "member_name": None,
        "enrollment_date": date(2022, 1, 1), "source_country": "IND"
    }])
    accepted, rejected = validate_members(df)
    assert len(accepted) == 0
    assert len(rejected) == 1
