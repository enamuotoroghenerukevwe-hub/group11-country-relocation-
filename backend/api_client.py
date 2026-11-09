"""CountryAPIClient: REST Countries v5 (free API key) with built-in sample data as a backup."""
from urllib.parse import quote

import requests

from backend.config import REST_COUNTRIES_URL
from backend.errors import APIRequestError, CountryNotFoundError
from backend.models import Country
from backend.offline_data import OFFLINE_COUNTRIES, search_offline
from backend.validators import CODE_PATTERN, validate_country_input


def explain_connection_error(error):
    """Turn a scary Python network error into a plain-English reason."""
    text = str(error)
    if any(w in text for w in ("getaddrinfo", "NameResolution", "Name or service not known", "Failed to resolve")):
        return "your device could not look up api.restcountries.com (DNS problem or blocked by your network/VPN)"
    if "refused" in text.lower():
        return "the connection was refused (firewall, antivirus or proxy may be blocking it)"
    if "reset" in text.lower() or "aborted" in text.lower():
        return "the connection was cut off (network, VPN or antivirus interference)"
    if "proxy" in text.lower():
        return "a proxy setting is getting in the way"
    return type(error).__name__


class CountryAPIClient:
    def __init__(self, api_key="", timeout=10):
        self.api_key = (api_key or "").strip()
        self.timeout = timeout
        self.note = ""          # message the UI shows when sample data was used

    def _get(self, path, params=None):
        """Call the API and return the list of country objects. Every failure becomes a clear error."""
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            response = requests.get(f"{REST_COUNTRIES_URL}{path}", headers=headers,
                                    params=params, timeout=self.timeout)
        except requests.exceptions.Timeout:
            raise APIRequestError("The country service took too long to answer.")
        except requests.exceptions.SSLError as error:
            raise APIRequestError(f"Secure connection to the country service failed ({type(error).__name__}).")
        except requests.exceptions.ConnectionError as error:
            raise APIRequestError(f"Could not reach api.restcountries.com: {explain_connection_error(error)}.")
        except requests.exceptions.RequestException as error:
            raise APIRequestError(f"Request failed: {error}")

        status = response.status_code
        if status in (400, 404):
            raise CountryNotFoundError("Country not found.")
        if status in (401, 403):
            raise APIRequestError("REST Countries rejected the API key (wrong key, or monthly limit used up).")
        if status == 429:
            raise APIRequestError("Too many requests. Wait a few seconds and try again.")
        if status != 200:
            raise APIRequestError(f"The country service returned an error ({status}).")
        try:
            data = response.json()["data"]
            return data.get("objects") or []
        except (ValueError, KeyError, AttributeError, TypeError):
            raise APIRequestError("The country service sent a response we could not read.")

    def _try(self, path, params=None):
        try:
            return self._get(path, params)
        except CountryNotFoundError:
            return []

    def _live_search(self, query):
        results = []
        if CODE_PATTERN.fullmatch(query) and len(query) in (2, 3):
            field = "codes.alpha_2" if len(query) == 2 else "codes.alpha_3"
            results = self._try(f"/{field}/{quote(query.upper())}")
        if not results:
            results = self._try(f"/names.common/{quote(query)}")
        if not results:
            results = self._try("/name", {"q": query, "limit": 25})
        if not results:
            raise CountryNotFoundError(f"No country found for '{query}'.")
        countries = [Country.from_api(item) for item in results]
        for country in countries:                       # prefer an exact name match
            if country.name.lower() == query.lower():
                return country
        return max(countries, key=lambda c: c.population or 0)

    def get_country(self, query):
        """Find one country by name or code. Falls back to sample data if the live API can't be used."""
        query = validate_country_input(query)
        sample_note = (f"Showing built-in sample data ({len(OFFLINE_COUNTRIES)} popular countries). "
                       "Add a free REST Countries API key in the sidebar to search all 250+.")

        if self.api_key:
            try:
                return self._live_search(query)
            except APIRequestError as error:
                fallback = search_offline(query)
                if not fallback:
                    raise
                self.note = f"Live data unavailable: {error} Showing built-in sample data instead."
                return fallback

        fallback = search_offline(query)
        if fallback:
            self.note = sample_note
            return fallback
        raise APIRequestError(f"'{query}' isn't in the built-in sample list. "
                              "Add a free REST Countries API key in the sidebar to search every country.")
