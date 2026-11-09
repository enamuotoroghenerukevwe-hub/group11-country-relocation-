"""Custom errors so the UI can show friendly messages."""


class CountryNotFoundError(Exception):
    """The country does not exist or could not be found."""


class APIRequestError(Exception):
    """An API call failed (timeout, no internet, bad response...)."""
