"""
components/search_bar.py
-------------------------
Reusable search input + submit button. Used on both the Home page (simple)
and Search page (with advanced options rendered separately).
"""

import streamlit as st

import config


def render_search_bar(key_prefix: str = "home", placeholder: str = None, button_label: str = "Search"):
    """
    Renders a search text input + button pair.

    Returns
    -------
    (query: str, submitted: bool)
    """
    placeholder = placeholder or "Ask about any recipe... e.g. \"fish curry with mustard paste\""

    with st.form(key=f"{key_prefix}_search_form", clear_on_submit=False):
        col1, col2 = st.columns([6, 1], vertical_alignment="bottom")
        with col1:
            query = st.text_input(
                "Search",
                value=st.session_state.get("query", ""),
                placeholder=placeholder,
                label_visibility="collapsed",
                key=f"{key_prefix}_query_input",
            )
        with col2:
            submitted = st.form_submit_button(f"{button_label}", use_container_width=True)

    return query, submitted


def render_example_queries(key_prefix: str = "home"):
    """Renders clickable example-query pills. Returns the clicked query, or None."""
    st.markdown('<div class="rag-section-label">Try asking</div>', unsafe_allow_html=True)
    clicked = None
    cols = st.columns(len(config.EXAMPLE_QUERIES))
    for i, (col, q) in enumerate(zip(cols, config.EXAMPLE_QUERIES)):
        with col:
            if st.button(q, key=f"{key_prefix}_example_{i}", use_container_width=True):
                clicked = q
    return clicked
