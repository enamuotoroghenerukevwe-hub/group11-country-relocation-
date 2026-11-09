"""Country Explorer - run with:  streamlit run app.py"""
import os
from types import SimpleNamespace

import streamlit as st

from backend.api_client import CountryAPIClient
from backend.guide import RelocationGuide
from backend.storage import Storage
from backend.validators import parse_utc_offset
from frontend import components as ui
from frontend import pages

def _secret(name):
    """Read a key from .streamlit/secrets.toml, or from an environment variable."""
    try:
        return st.secrets.get(name, "") or os.getenv(name, "")
    except Exception:
        return os.getenv(name, "")


st.set_page_config(page_title="Country Explorer", page_icon="", initial_sidebar_state="collapsed")
ui.load_css()

# Remembered values between clicks
st.session_state.setdefault("page", "Home")
for key in ("country", "guide", "compare"):
    st.session_state.setdefault(key, None)

# Sidebar settings
with st.sidebar:
    st.header("🛂 Settings")
    rc_key = st.text_input("REST Countries API key (free)", type="password",
                           value=_secret("RESTCOUNTRIES_API_KEY"),
                           help="Get one free at restcountries.com/sign-up. Without it the app uses built-in sample data.")
    gemini_key = st.text_input("Gemini API key (optional)", type="password", value=_secret("GEMINI_API_KEY"))
    home_tz_text = st.text_input("Your timezone", value="UTC", help="Format: UTC+01:00")
    try:
        parse_utc_offset(home_tz_text)
        home_tz = home_tz_text.upper()
    except ValueError as error:
        st.warning(str(error))
        home_tz = None

ctx = SimpleNamespace(client=CountryAPIClient(rc_key), guide=RelocationGuide(gemini_key),
                      storage=Storage(), home_tz=home_tz)

PAGES = {"Home": pages.home, "Explore": pages.explore, "Compare": pages.compare, "Saved": pages.saved}
st.radio("Navigate", list(PAGES), key="page", horizontal=True, label_visibility="collapsed")
PAGES[st.session_state.page](ctx)

st.markdown('<div class="footer">Data: REST Countries · Guides: Gemini · Saved locally in /data</div>',
            unsafe_allow_html=True)
