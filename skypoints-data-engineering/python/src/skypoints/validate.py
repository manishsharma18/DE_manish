
import pandas as pd

REQUIRED = ["member_id", "member_name", "enrollment_date"]
MAX_LENGTHS = {"member_id": 18, "member_name": 255, "tier_code": 5,
               "state": 5, "country": 5, "agent_name": 255}

def validate_members(df: pd.DataFrame):
    work = df.copy()
    reasons = [[] for _ in range(len(work))]

    for idx, row in work.iterrows():
        pos = work.index.get_loc(idx)
        for col in REQUIRED:
            if pd.isna(row.get(col)) or row.get(col) in ("", None):
                reasons[pos].append(f"MISSING_REQUIRED_{col.upper()}")
        for col, max_len in MAX_LENGTHS.items():
            val = row.get(col)
            if pd.notna(val) and len(str(val)) > max_len:
                reasons[pos].append(f"{col.upper()}_EXCEEDS_{max_len}")
        if pd.notna(row.get("date_of_birth")) and pd.notna(row.get("enrollment_date")):
            if row["date_of_birth"] >= row["enrollment_date"]:
                reasons[pos].append("DOB_NOT_BEFORE_ENROLLMENT")
        if pd.notna(row.get("last_flight_date")) and pd.notna(row.get("enrollment_date")):
            if row["last_flight_date"] < row["enrollment_date"]:
                reasons[pos].append("FLIGHT_BEFORE_ENROLLMENT")

    work["reject_reason"] = [";".join(r) for r in reasons]
    # Duplicate key within a country is invalid; across country feeds is permitted
    # pending confirmation of global member-ID uniqueness.
    dup = work.duplicated(["source_country", "member_id"], keep=False)
    work.loc[dup & work["reject_reason"].eq(""), "reject_reason"] = "DUPLICATE_COUNTRY_MEMBER_KEY"
    accepted = work[work["reject_reason"].eq("")].drop(columns=["reject_reason"])
    rejected = work[~work["reject_reason"].eq("")]
    return accepted, rejected
