from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
DEMO_SIGNALS_PATH = DATA_DIR / "demo_signals.csv"
WORLD_GEOJSON_PATH = DATA_DIR / "world_countries.geojson"
APP_TITLE = "SentinelFS Atlas"
COMMODITIES = ["Wheat", "Rice", "Corn"]
WINDOW_OPTIONS = [30, 90]
