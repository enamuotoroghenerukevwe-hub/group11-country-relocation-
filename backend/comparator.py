"""CountryComparator: compares two Country objects."""
from backend.validators import describe_difference, hours_difference


class CountryComparator:
    def __init__(self, country_a, country_b):
        self.a = country_a
        self.b = country_b

    def rows(self):
        a, b = self.a, self.b
        return [
            ("Capital", a.capital_text, b.capital_text),
            ("Region", a.region, b.region),
            ("Subregion", a.subregion, b.subregion),
            ("Population", a.population_text, b.population_text),
            ("Currency", a.currency_text, b.currency_text),
            ("Languages", a.language_text, b.language_text),
            ("Main timezone", a.main_timezone or "N/A", b.main_timezone or "N/A"),
        ]

    def timezone_difference(self):
        """Sentence about B's time compared with A, or None if unknown."""
        if not (self.a.main_timezone and self.b.main_timezone):
            return None
        try:
            hours = hours_difference(self.a.main_timezone, self.b.main_timezone)
        except ValueError:
            return None
        return f"{self.b.name} is {describe_difference(hours, self.a.name)}."

    def population_note(self):
        pa, pb = self.a.population, self.b.population
        if isinstance(pa, int) and isinstance(pb, int) and pb:
            return f"{self.a.name} has {pa / pb:.1f}x the population of {self.b.name}."
        return None

    def to_dict(self):
        return {
            "country_a": self.a.name,
            "country_b": self.b.name,
            "rows": [{"field": f, "a": x, "b": y} for f, x, y in self.rows()],
            "timezone_difference": self.timezone_difference(),
            "population_note": self.population_note(),
        }
