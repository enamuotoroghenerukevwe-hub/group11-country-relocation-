"""RelocationGuide: AI guide (Gemini) + 'before you travel' checklist."""
import requests

from backend.config import GEMINI_URL
from backend.errors import APIRequestError
from backend.validators import describe_difference, hours_difference


class RelocationGuide:
    PURPOSES = ["Travel", "Study", "Relocation"]

    def __init__(self, gemini_key=""):
        self.gemini_key = gemini_key

    def _prompt(self, country, purpose):
        return (
            f"You are a friendly advisor. Write a short, simple {purpose.lower()} guide "
            f"(under 300 words) for someone going to {country.name}.\n"
            f"Facts: capital {country.capital_text}; currency {country.currency_text}; "
            f"languages {country.language_text}; population {country.population_text}; "
            f"region {country.region} ({country.subregion}); timezone {country.main_timezone}.\n"
            "Use short headings: Overview, Money, Language, Daily life, Tips. Plain language. "
            "End by reminding the reader to check official government sources for visa rules."
        )

    def _call_gemini(self, prompt):
        headers = {"Content-Type": "application/json", "x-goog-api-key": self.gemini_key}
        body = {"contents": [{"parts": [{"text": prompt}]}]}
        try:
            response = requests.post(GEMINI_URL, headers=headers, json=body, timeout=30)
        except requests.exceptions.RequestException:
            raise APIRequestError("Could not reach the Gemini API.")
        if response.status_code in (400, 401, 403):
            raise APIRequestError("Gemini rejected the request. Check your API key.")
        if response.status_code != 200:
            raise APIRequestError(f"Gemini returned an error ({response.status_code}).")
        try:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, ValueError):
            raise APIRequestError("Gemini sent an unexpected response.")

    def _offline_guide(self, country, purpose):
        return (
            f"{purpose} guide: {country.name}\n\n"
            f"Overview\n{country.name} is in {country.subregion} ({country.region}). "
            f"The capital is {country.capital_text}; about {country.population_text} people live there.\n\n"
            f"Money\nCurrency: {country.currency_text}. Check card fees and exchange rates.\n\n"
            f"Language\nPeople speak {country.language_text}. Learn a few basic phrases.\n\n"
            f"Time\nMain timezone: {country.main_timezone or 'not available'}.\n\n"
            "Tip\nCheck official government websites for visa and entry rules."
        )

    def generate(self, country, purpose):
        """Return (guide_text, note). Falls back to a simple guide if AI is unavailable."""
        if not self.gemini_key:
            return self._offline_guide(country, purpose), "Simple offline guide. Add a Gemini key in the sidebar for AI."
        try:
            return self._call_gemini(self._prompt(country, purpose)), "Written by Gemini AI"
        except APIRequestError as error:
            return self._offline_guide(country, purpose), f"AI unavailable ({error}) Showing a simple guide."

    def checklist(self, country, home_tz=None):
        items = [
            "Check your passport is valid for at least 6 months",
            f"Check visa / entry rules for {country.name} on the official government website",
            "Buy travel insurance",
            "Book flights and accommodation",
            f"Get some {country.currencies[0] if country.currencies else 'local currency'} and tell your bank you're travelling",
            f"Learn a few phrases in {country.languages[0] if country.languages else 'the local language'}",
            "Check vaccination or health requirements",
            "Sort out phone roaming or an eSIM",
            "Pack the right power adapter",
            "Save copies of your documents and emergency contacts",
        ]
        if home_tz and country.main_timezone:
            try:
                diff = hours_difference(home_tz, country.main_timezone)
                if abs(diff) >= 3:
                    items.append(f"Shift your sleep a few days early ({country.name} is {describe_difference(diff)})")
            except ValueError:
                pass
        return items
