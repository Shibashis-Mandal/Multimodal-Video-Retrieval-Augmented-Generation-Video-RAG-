"""
utils/session_state.py
-----------------------
Central place that defines what lives in st.session_state and how it's
initialized. Import `init_session_state()` at the top of every page so state
is guaranteed to exist no matter which page the user lands on first
(Streamlit multipage apps can be entered from any page via the sidebar/URL).

STATE KEYS
----------
query            : str   - the current/last submitted search query
results          : dict  - last response from api_client.search_videos()
selected_video   : str   - video_id currently open on the Results page
search_history   : list  - session-local list of past queries (most recent first)
theme            : str   - "dark" | "light"
top_k            : int   - advanced search option
rerank_enabled   : bool  - advanced search option
hybrid_enabled   : bool  - advanced search option
language         : str   - selected search language
is_searching     : bool  - drives the loading state
"""

import streamlit as st

import config
import dummy_data


DEFAULTS = {
    "query": "",
    "results": None,
    "selected_video": None,
    "search_history": None,  # lazily seeded from dummy_data on first init
    "theme": "dark",
    "top_k": config.DEFAULT_TOP_K,
    "rerank_enabled": config.DEFAULT_RERANK,
    "hybrid_enabled": config.DEFAULT_HYBRID,
    "language": config.SUPPORTED_LANGUAGES[0],
    "is_searching": False,
}


def init_session_state():
    """Populate any missing session_state keys with sensible defaults."""
    for key, default in DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = default

    if st.session_state["search_history"] is None:
        st.session_state["search_history"] = [
            item["query"] for item in dummy_data.mock_get_history()
        ]


def push_search_history(query: str):
    """Add a query to the front of the session's recent-searches list."""
    if not query:
        return
    history = st.session_state.get("search_history", [])
    history = [q for q in history if q.lower() != query.lower()]
    history.insert(0, query)
    st.session_state["search_history"] = history[:10]


def set_results(results: dict):
    st.session_state["results"] = results
    if results and results.get("results"):
        st.session_state["selected_video"] = results["results"][0]["video_id"]


def get_theme_colors():
    """Return the active color dict for the current theme."""
    return config.THEME[st.session_state.get("theme", "dark")]
