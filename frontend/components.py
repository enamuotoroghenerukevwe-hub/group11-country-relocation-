"""Reusable UI pieces."""
from html import escape
from pathlib import Path

import streamlit as st

from backend.validators import current_time_at, describe_difference, hours_difference


def load_css():
    css = (Path(__file__).parent / "styles.css").read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def _tile(label, value):
    return f'<div class="tile"><small>{escape(label)}</small><div>{escape(value)}</div></div>'


def country_card(country, home_tz):
    """The passport-style card showing a country's details."""
    time_text = "Not available"
    if country.main_timezone:
        time_text = country.main_timezone
        try:
            time_text += f" · now {current_time_at(country.main_timezone)}"
            if home_tz:
                time_text += f" · {describe_difference(hours_difference(home_tz, country.main_timezone))}"
        except ValueError:
            pass
    tiles = "".join([
        _tile("Capital", country.capital_text),
        _tile("Region", f"{country.region} · {country.subregion}"),
        _tile("Population", country.population_text),
        _tile("Currency", country.currency_text),
        _tile("Languages", country.language_text),
        _tile("Timezone", time_text),
    ])
    flag = f'<img src="{escape(country.flag_url)}" alt="flag">' if country.flag_url else ""
    st.markdown(
        f'<div class="passport"><div class="passport-head">{flag}<div>'
        f'<div class="official">{escape(country.official_name)}</div><h2>{escape(country.name)}</h2></div>'
        f'<div class="stamp">{escape(country.code)}</div></div><div class="tiles">{tiles}</div></div>',
        unsafe_allow_html=True,
    )


def compare_table(comparator):
    head = (f"<tr><th></th><th>{escape(comparator.a.name)}</th><th>{escape(comparator.b.name)}</th></tr>")
    body = "".join(f"<tr><td>{escape(f)}</td><td>{escape(x)}</td><td>{escape(y)}</td></tr>"
                   for f, x, y in comparator.rows())
    st.markdown(f'<div class="vs-wrap"><table class="vs">{head}{body}</table></div>', unsafe_allow_html=True)


def checklist(ctx, country, key):
    """Tick-box checklist with a save-to-file button."""
    items = ctx.guide.checklist(country, ctx.home_tz)
    for i, item in enumerate(items):
        st.checkbox(item, key=f"{key}_{i}")
    if st.button("💾 Save checklist to file", key=f"{key}_save"):
        text = f"Before you travel to {country.name}\n\n" + "\n".join(f"[ ] {x}" for x in items)
        st.success(f"Saved to {ctx.storage.save_text('checklist', country.name, text)}")
