"""Storage: saves and loads files in the data/ folder."""
import json
import re
from datetime import datetime

from backend.config import DATA_DIR, FAVOURITES_FILE


class Storage:
    def __init__(self):
        DATA_DIR.mkdir(exist_ok=True)

    @staticmethod
    def _filename(prefix, name, ext):
        safe = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
        return DATA_DIR / f"{prefix}_{safe}_{datetime.now():%Y%m%d_%H%M%S}.{ext}"

    def save_text(self, prefix, name, content):
        path = self._filename(prefix, name, "txt")
        path.write_text(content, encoding="utf-8")
        return path

    def save_json(self, prefix, name, data):
        path = self._filename(prefix, name, "json")
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return path

    def load_favourites(self):
        """Saved favourites as a dict. A missing or damaged file gives {}."""
        try:
            return json.loads(FAVOURITES_FILE.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _write_favourites(self, favourites):
        FAVOURITES_FILE.write_text(json.dumps(favourites, indent=2, ensure_ascii=False), encoding="utf-8")

    def save_favourite(self, country, guide_text=""):
        favourites = self.load_favourites()
        favourites[country.code] = {"profile": country.to_dict(), "guide": guide_text}
        self._write_favourites(favourites)

    def remove_favourite(self, code):
        favourites = self.load_favourites()
        favourites.pop(code, None)
        self._write_favourites(favourites)
