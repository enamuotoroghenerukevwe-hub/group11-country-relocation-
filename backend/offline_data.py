"""Built-in sample data (26 popular countries, approximate populations).
Used when there is no REST Countries API key or the live service can't be reached."""
from backend.models import FLAG_CDN, Country

# name, code, capital, currency, languages, timezone, population, region, subregion
_ROWS = [
    ("Nigeria", "NG", "Abuja", "Nigerian naira (NGN ₦)", "English", "UTC+01:00", 223800000, "Africa", "Western Africa"),
    ("Ghana", "GH", "Accra", "Ghanaian cedi (GHS ₵)", "English", "UTC", 34100000, "Africa", "Western Africa"),
    ("Kenya", "KE", "Nairobi", "Kenyan shilling (KES KSh)", "English, Swahili", "UTC+03:00", 55100000, "Africa", "Eastern Africa"),
    ("South Africa", "ZA", "Pretoria", "South African rand (ZAR R)", "Afrikaans, English, Zulu, Xhosa", "UTC+02:00", 60400000, "Africa", "Southern Africa"),
    ("Egypt", "EG", "Cairo", "Egyptian pound (EGP £)", "Arabic", "UTC+02:00", 112700000, "Africa", "Northern Africa"),
    ("United States", "US", "Washington, D.C.", "United States dollar (USD $)", "English", "UTC-05:00", 335000000, "Americas", "Northern America"),
    ("Canada", "CA", "Ottawa", "Canadian dollar (CAD $)", "English, French", "UTC-05:00", 40100000, "Americas", "Northern America"),
    ("Mexico", "MX", "Mexico City", "Mexican peso (MXN $)", "Spanish", "UTC-06:00", 128500000, "Americas", "North America"),
    ("Brazil", "BR", "Brasília", "Brazilian real (BRL R$)", "Portuguese", "UTC-03:00", 216400000, "Americas", "South America"),
    ("United Kingdom", "GB", "London", "Pound sterling (GBP £)", "English", "UTC", 67700000, "Europe", "Northern Europe"),
    ("France", "FR", "Paris", "Euro (EUR €)", "French", "UTC+01:00", 68200000, "Europe", "Western Europe"),
    ("Germany", "DE", "Berlin", "Euro (EUR €)", "German", "UTC+01:00", 84500000, "Europe", "Western Europe"),
    ("Italy", "IT", "Rome", "Euro (EUR €)", "Italian", "UTC+01:00", 58900000, "Europe", "Southern Europe"),
    ("Spain", "ES", "Madrid", "Euro (EUR €)", "Spanish", "UTC+01:00", 48100000, "Europe", "Southern Europe"),
    ("Portugal", "PT", "Lisbon", "Euro (EUR €)", "Portuguese", "UTC", 10400000, "Europe", "Southern Europe"),
    ("Netherlands", "NL", "Amsterdam", "Euro (EUR €)", "Dutch", "UTC+01:00", 17900000, "Europe", "Western Europe"),
    ("Turkey", "TR", "Ankara", "Turkish lira (TRY ₺)", "Turkish", "UTC+03:00", 85300000, "Asia", "Western Asia"),
    ("United Arab Emirates", "AE", "Abu Dhabi", "UAE dirham (AED)", "Arabic", "UTC+04:00", 9500000, "Asia", "Western Asia"),
    ("India", "IN", "New Delhi", "Indian rupee (INR ₹)", "Hindi, English", "UTC+05:30", 1428600000, "Asia", "Southern Asia"),
    ("China", "CN", "Beijing", "Chinese yuan (CNY ¥)", "Chinese", "UTC+08:00", 1410700000, "Asia", "Eastern Asia"),
    ("Japan", "JP", "Tokyo", "Japanese yen (JPY ¥)", "Japanese", "UTC+09:00", 123300000, "Asia", "Eastern Asia"),
    ("South Korea", "KR", "Seoul", "South Korean won (KRW ₩)", "Korean", "UTC+09:00", 51700000, "Asia", "Eastern Asia"),
    ("Singapore", "SG", "Singapore", "Singapore dollar (SGD $)", "English, Malay, Chinese, Tamil", "UTC+08:00", 5900000, "Asia", "South-Eastern Asia"),
    ("Vietnam", "VN", "Hanoi", "Vietnamese đồng (VND ₫)", "Vietnamese", "UTC+07:00", 98900000, "Asia", "South-Eastern Asia"),
    ("Australia", "AU", "Canberra", "Australian dollar (AUD $)", "English", "UTC+10:00", 26600000, "Oceania", "Australia and New Zealand"),
    ("New Zealand", "NZ", "Wellington", "New Zealand dollar (NZD $)", "English, Māori", "UTC+12:00", 5200000, "Oceania", "Australia and New Zealand"),
]

ALIASES = {"usa": "US", "us": "US", "america": "US", "uk": "GB", "britain": "GB", "england": "GB", "uae": "AE"}

OFFLINE_COUNTRIES = [
    Country(n, n, cc, [cap], [cur], langs.split(", "), pop, reg, sub, FLAG_CDN.format(cc.lower()), [tz])
    for n, cc, cap, cur, langs, tz, pop, reg, sub in _ROWS
]


def search_offline(query):
    """Find a country in the built-in list by name, code or common nickname."""
    q = query.strip().lower()
    code = ALIASES.get(q) or (q.upper() if len(q) == 2 else None)
    for country in OFFLINE_COUNTRIES:
        if country.code == code or country.name.lower() == q:
            return country
    if len(q) >= 3:
        for country in OFFLINE_COUNTRIES:
            if q in country.name.lower():
                return country
    return None
