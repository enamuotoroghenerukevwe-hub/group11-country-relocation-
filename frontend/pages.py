"""The four pages: Home, Explore, Compare, Saved."""
import streamlit as st

from backend.comparator import CountryComparator
from backend.errors import APIRequestError, CountryNotFoundError
from backend.guide import RelocationGuide
from backend.models import Country
from frontend import components as ui

POPULAR = ["Japan", "Brazil", "Canada", "Kenya", "Italy", "New Zealand"]


def go(page, query=""):
    """Button callback: jump to a page (and optionally search straight away)."""
    st.session_state.page = page
    if query:
        st.session_state.explore_q = query
        st.session_state.run_search = True


def _show_note():
    if st.session_state.get("source_note"):
        st.info(st.session_state.source_note)


def _home_search():
    go("Explore", st.session_state.get("home_q", ""))


def home(ctx):
    st.markdown(
        '<div class="hero"><span class="pill">✈ Your pocket atlas</span>'
        '<h1>Where to <em>next?</em></h1>'
        '<p>Look up any country, get an AI-written guide, compare two places and keep a passport of favourites.</p></div>',
        unsafe_allow_html=True)
    st.text_input("Search", key="home_q", placeholder="Try Portugal, KE or Vietnam…", label_visibility="collapsed")
    st.button("Explore →", type="primary", on_click=_home_search)

    st.markdown('<div class="label">Popular right now</div>', unsafe_allow_html=True)
    for row in range(0, len(POPULAR), 3):
        cols = st.columns(3)
        for col, name in zip(cols, POPULAR[row:row + 3]):
            col.button(name, key=f"pop_{name}", on_click=go, args=("Explore", name), use_container_width=True)

    st.markdown(
        '<div class="features">'
        '<div class="feature">🧭<b>Instant profiles</b><span>Capital, currency, languages, flag and more.</span></div>'
        '<div class="feature">✨<b>AI guides</b><span>Travel, study or relocation tips from Gemini.</span></div>'
        '<div class="feature">⚖️<b>Side by side</b><span>Compare two countries and the time gap.</span></div>'
        '</div>', unsafe_allow_html=True)


def explore(ctx):
    st.markdown("## 🔎 Explore")
    st.text_input("Country name or code", key="explore_q", placeholder="e.g. Japan or NG")
    purpose = st.selectbox("I'm planning to…", RelocationGuide.PURPOSES)

    if st.button("Search", type="primary") or st.session_state.pop("run_search", False):
        try:
            st.session_state.country = ctx.client.get_country(st.session_state.explore_q)
            st.session_state.guide = None
            st.session_state.source_note = ctx.client.note
        except ValueError as error:
            st.error(str(error))
        except CountryNotFoundError:
            st.error("We couldn't find that country. Check the spelling and try again.")
        except APIRequestError as error:
            st.error(str(error))

    country = st.session_state.country
    if not country:
        return
    _show_note()
    ui.country_card(country, ctx.home_tz)

    if st.button("✨ Generate guide"):
        with st.spinner("Writing your guide…"):
            st.session_state.guide, st.session_state.guide_note = ctx.guide.generate(country, purpose)
    if st.session_state.guide:
        st.caption(st.session_state.get("guide_note", ""))
        st.write(st.session_state.guide)
        st.download_button("⬇️ Download guide", st.session_state.guide, file_name=f"{country.name}_guide.txt")

    with st.expander("✅ Before you travel checklist"):
        ui.checklist(ctx, country, "explore_check")
    if st.button("⭐ Save to favourites"):
        ctx.storage.save_favourite(country, st.session_state.guide or "")
        st.success(f"{country.name} saved to your passport!")


def compare(ctx):
    st.markdown("## ⚖️ Compare")
    col1, col2 = st.columns(2)
    name_a = col1.text_input("From (home)", key="cmp_a", placeholder="e.g. Nigeria")
    name_b = col2.text_input("To (destination)", key="cmp_b", placeholder="e.g. Canada")

    if st.button("Compare", type="primary"):
        try:
            country_a = ctx.client.get_country(name_a)
            country_b = ctx.client.get_country(name_b)
            st.session_state.compare = CountryComparator(country_a, country_b)
            st.session_state.source_note = ctx.client.note
        except ValueError as error:
            st.error(str(error))
        except CountryNotFoundError:
            st.error("One of those countries could not be found.")
        except APIRequestError as error:
            st.error(str(error))

    cmp = st.session_state.compare
    if not cmp:
        return
    _show_note()
    ui.compare_table(cmp)
    for note in (cmp.timezone_difference(), cmp.population_note()):
        if note:
            st.markdown(f'<div class="callout">{note}</div>', unsafe_allow_html=True)
    if st.button("💾 Save comparison to file"):
        path = ctx.storage.save_json("comparison", f"{cmp.a.name}_vs_{cmp.b.name}", cmp.to_dict())
        st.success(f"Saved to {path}")
    st.markdown(f"### ✅ Before you travel to {cmp.b.name}")
    ui.checklist(ctx, cmp.b, "cmp_check")


def saved(ctx):
    st.markdown("## ⭐ Your passport")
    favourites = ctx.storage.load_favourites()
    if not favourites:
        st.write("No favourites yet. Explore a country and tap ⭐ Save.")
    for code, entry in list(favourites.items()):
        try:
            country = Country.from_dict(entry["profile"])
        except (KeyError, TypeError):
            st.warning(f"Skipped a damaged entry ({code}).")
            continue
        with st.expander(f"{country.name} ({code})"):
            ui.country_card(country, ctx.home_tz)
            if entry.get("guide"):
                st.write(entry["guide"])
            if st.button("🗑️ Remove", key=f"remove_{code}"):
                ctx.storage.remove_favourite(code)
                st.rerun()
