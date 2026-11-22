
from pathlib import Path
import pandas as pd
from .config import INPUT_DIR, REDEMPTION_DIR, OUTPUT_DIR, COUNTRY_BY_FILE
from .ingest import read_member_workbooks, flatten_redemption_json

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    accepted, rejected = read_member_workbooks(INPUT_DIR, COUNTRY_BY_FILE)
    accepted.to_csv(OUTPUT_DIR / "member_normalized.csv", index=False)
    rejected.to_csv(OUTPUT_DIR / "member_rejects.csv", index=False)

    redemption_frames = []
    if REDEMPTION_DIR.exists():
        for path in sorted(REDEMPTION_DIR.glob("*.json")):
            frame = flatten_redemption_json(path)
            frame["source_file"] = path.name
            redemption_frames.append(frame)
    redemptions = pd.concat(redemption_frames, ignore_index=True) if redemption_frames else pd.DataFrame()
    redemptions.to_csv(OUTPUT_DIR / "redemptions_flat.csv", index=False)

    print(f"Accepted member rows: {len(accepted)}")
    print(f"Rejected member rows: {len(rejected)}")
    print(f"Flattened redemption rows: {len(redemptions)}")
    print(f"Output directory: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
