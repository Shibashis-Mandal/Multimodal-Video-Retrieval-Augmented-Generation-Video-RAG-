"""
pages/3_Settings.py
--------------------
User-adjustable preferences: theme, default search behavior. Also surfaces
the current mock/backend mode (read-only here; toggled in config.py).
"""

import streamlit as st

import config
from utils.session_state import init_session_state
from components.header import inject_theme, render_page_header
from components.sidebar import render_sidebar
from components.footer import render_footer

st.set_page_config(page_title=f"Settings · {config.APP_NAME}", page_icon=config.APP_ICON, layout="wide")

init_session_state()
inject_theme()
render_sidebar()

render_page_header("Settings", "Personalize how RecipeRAG looks and searches by default.")

col1, col2, col3 = st.columns([1, 4, 1])
with col2:
    st.markdown('<div class="rag-card">', unsafe_allow_html=True)
    st.markdown("#### Appearance")
    theme_choice = st.radio(
        "Theme",
        options=["dark", "light"],
        index=0 if st.session_state["theme"] == "dark" else 1,
        format_func=lambda t: "🌙 Dark" if t == "dark" else "☀️ Light",
        horizontal=True,
    )
    if theme_choice != st.session_state["theme"]:
        st.session_state["theme"] = theme_choice
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="rag-card">', unsafe_allow_html=True)
    st.markdown("#### Default Search Behavior")
    st.session_state["top_k"] = st.slider(
        "Default Top-K results", config.MIN_TOP_K, config.MAX_TOP_K, st.session_state["top_k"]
    )
    st.session_state["rerank_enabled"] = st.toggle(
        "Re-ranking enabled by default", value=st.session_state["rerank_enabled"]
    )
    st.session_state["hybrid_enabled"] = st.toggle(
        "Hybrid search enabled by default", value=st.session_state["hybrid_enabled"]
    )
    st.session_state["language"] = st.selectbox(
        "Default language",
        options=config.SUPPORTED_LANGUAGES,
        index=config.SUPPORTED_LANGUAGES.index(st.session_state["language"]),
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="rag-card">', unsafe_allow_html=True)
    st.markdown("#### Backend Connection")
    st.write(f"**Mode:** {'🧪 Mock data' if config.USE_MOCK_DATA else '🔌 Live API'}")
    st.write(f"**API base URL:** `{config.API_BASE_URL}`")
    st.caption(
        "This is controlled by `USE_MOCK_DATA` in config.py, not from this page — "
        "keeping it a deploy-time/code setting avoids accidentally pointing a "
        "shared session at the wrong backend."
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="rag-card">', unsafe_allow_html=True)
    st.markdown("#### Session Data")
    if st.button("Clear search history"):
        st.session_state["search_history"] = []
        st.success("Search history cleared.")
    if st.button("Reset all settings to defaults"):
        for key in ["top_k", "rerank_enabled", "hybrid_enabled", "language", "theme"]:
            del st.session_state[key]
        init_session_state()
        st.success("Settings reset.")
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

render_footer()
