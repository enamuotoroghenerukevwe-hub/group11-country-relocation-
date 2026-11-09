"""Regular expressions for checking input + timezone helpers."""
import re
from datetime import datetime, timedelta, timezone

NAME_PATTERN = re.compile(r"[A-Za-zÀ-ÿ' .\-]{2,60}")                 # "Côte d'Ivoire"
CODE_PATTERN = re.compile(r"[A-Za-z]{2,3}")                           # "NG" or "NGA"
TIMEZONE_PATTERN = re.compile(r"UTC(?:([+-])(\d{2}):(\d{2}))?")       # "UTC" or "UTC+05:30"


def validate_country_input(text):
    """Clean the text and make sure it looks like a country name or code."""
    text = " ".join((text or "").split())
    if not text:
        raise ValueError("Please type a country name or code.")
    if not (NAME_PATTERN.fullmatch(text) or CODE_PATTERN.fullmatch(text)):
        raise ValueError("Use letters only (for example: Japan, Brazil or NG).")
    return text


def parse_utc_offset(tz_text):
    """'UTC+05:30' -> timedelta. Raises ValueError for a bad format."""
    match = TIMEZONE_PATTERN.fullmatch((tz_text or "").strip().upper())
    if not match:
        raise ValueError(f"'{tz_text}' is not a valid timezone. Use a format like UTC+01:00.")
    sign, hours, minutes = match.groups()
    if sign is None:
        return timedelta(0)
    offset = timedelta(hours=int(hours), minutes=int(minutes))
    return -offset if sign == "-" else offset


def hours_difference(home_tz, other_tz):
    """Hours that other_tz is ahead (+) or behind (-) home_tz."""
    return (parse_utc_offset(other_tz) - parse_utc_offset(home_tz)).total_seconds() / 3600


def describe_difference(hours, home_label="home"):
    if hours == 0:
        return f"the same time as {home_label}"
    direction = "ahead of" if hours > 0 else "behind"
    return f"{abs(hours):g} hour(s) {direction} {home_label}"


def current_time_at(tz_text):
    """Local time right now for a timezone like 'UTC+02:00'."""
    return (datetime.now(timezone.utc) + parse_utc_offset(tz_text)).strftime("%a %H:%M")
