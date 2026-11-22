
import json
import pandas as pd
from .normalize import normalize_frame
from .validate import validate_members

def read_member_workbooks(input_dir, country_by_file, as_of=None):
    frames = []
    for filename, country in country_by_file.items():
        path = input_dir / filename
        if not path.exists():
            continue
        raw = pd.read_excel(path, dtype=object)
        frames.append(normalize_frame(raw, country, filename, as_of=as_of))
    if not frames:
        return pd.DataFrame(), pd.DataFrame()
    combined = pd.concat(frames, ignore_index=True)
    return validate_members(combined)

def flatten_redemption_json(path):
    """One row per redemption; raw payload can also be retained in Snowflake VARIANT."""
    with open(path, encoding="utf-8") as f:
        payload = json.load(f)
    rows = []
    for txn in payload.get("redemptions", []):
        rows.append({
            "member_id": str(payload.get("member_id", "")).strip(),
            "feed_date": payload.get("feed_date"),
            "txn_id": txn.get("txn_id"),
            "txn_date": txn.get("txn_date"),
            "partner": txn.get("partner"),
            "miles_redeemed": txn.get("miles_redeemed"),
            "status": txn.get("status"),
        })
    return pd.DataFrame(rows)
