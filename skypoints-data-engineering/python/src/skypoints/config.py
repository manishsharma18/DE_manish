
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
INPUT_DIR = PROJECT_ROOT / "data" / "input"
REDEMPTION_DIR = PROJECT_ROOT / "data" / "redemption"
OUTPUT_DIR = PROJECT_ROOT / "output"

# Country is deliberately derived from the supplied workbook name.
COUNTRY_BY_FILE = {"IND.xlsx": "IND", "USA.xlsx": "USA", "AUS.xlsx": "AUS"}
