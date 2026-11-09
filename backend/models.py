"""The Country class: holds the details of one country."""

FLAG_CDN = "https://flags.restcountries.com/v5/w320/{}.png"     # free, no key needed


def _first_text(item, keys):
    """Return the first non-empty text value found under any of the keys."""
    for key in keys:
        if isinstance(item.get(key), str) and item[key]:
            return item[key]
    return None


class Country:
    def __init__(self, name, official_name, code, capitals, currencies,
                 languages, population, region, subregion, flag_url, timezones):
        self.name = name
        self.official_name = official_name
        self.code = code
        self.capitals = capitals
        self.currencies = currencies
        self.languages = languages
        self.population = population
        self.region = region
        self.subregion = subregion
        self.flag_url = flag_url
        self.timezones = timezones

    @staticmethod
    def _read_currencies(raw):
        if isinstance(raw, dict):   # {"CAD": {"name": ..., "symbol": ...}}
            raw = [dict(v, code=k) if isinstance(v, dict) else {"code": k, "name": str(v)} for k, v in raw.items()]
        result = []
        for item in raw or []:
            if not isinstance(item, dict):
                result.append(str(item))
                continue
            code, symbol = item.get("code", ""), item.get("symbol", "")
            name = _first_text(item, ["name", "english_name"]) or code
            result.append(f"{name} ({code}{' ' + symbol if symbol else ''})" if code else name)
        return result

    @staticmethod
    def _read_languages(raw):
        if isinstance(raw, dict):
            raw = list(raw.values())
        result = []
        for item in raw or []:
            name = _first_text(item, ["name", "english_name", "english", "native_name", "native"]) \
                if isinstance(item, dict) else str(item)
            if name:
                result.append(name)
        return result

    @classmethod
    def from_api(cls, data):
        """Build a Country from REST Countries v5 JSON. Missing fields get safe defaults."""
        names, codes, flag = data.get("names") or {}, data.get("codes") or {}, data.get("flag") or {}
        code = codes.get("alpha_2") or "??"
        capitals = [c.get("name") if isinstance(c, dict) else str(c) for c in data.get("capitals") or []]
        population = data.get("population")
        return cls(
            name=names.get("common") or "Unknown",
            official_name=names.get("official") or names.get("common") or "Unknown",
            code=code,
            capitals=[c for c in capitals if c],
            currencies=cls._read_currencies(data.get("currencies")),
            languages=cls._read_languages(data.get("languages")),
            population=int(population) if isinstance(population, (int, float)) else None,
            region=data.get("region") or "Unknown",
            subregion=data.get("subregion") or "Unknown",
            flag_url=flag.get("url_png") or (FLAG_CDN.format(code.lower()) if code != "??" else ""),
            timezones=data.get("timezones") or [],
        )

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def to_dict(self):
        return dict(self.__dict__)

    @property
    def capital_text(self):
        return ", ".join(self.capitals) or "Not available"

    @property
    def currency_text(self):
        return ", ".join(self.currencies) or "Not available"

    @property
    def language_text(self):
        return ", ".join(self.languages) or "Not available"

    @property
    def population_text(self):
        return f"{self.population:,}" if isinstance(self.population, int) else "Not available"

    @property
    def main_timezone(self):
        return self.timezones[0] if self.timezones else None
