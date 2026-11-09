"""Settings used across the backend."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"                       # all saved files live here
FAVOURITES_FILE = DATA_DIR / "favourites.json"

REST_COUNTRIES_URL = "https://api.restcountries.com/countries/v5"   # v5 (v1-v4 were shut down)

GEMINI_MODEL = "gemini-flash-latest"          # the model name from your Google example
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
