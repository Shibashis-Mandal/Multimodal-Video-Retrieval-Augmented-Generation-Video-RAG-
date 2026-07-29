"""
pages/1_Search.py
------------------
Full search experience: large input, language selector, advanced options
(top-K, re-ranking, hybrid search), loading state, then hands off to the
Results page once a search completes.
"""

import streamlit as st

import config
from utils.session_state import init_session_state, push_search_history, set_results
from utils.api_client import search_videos, APIError
from components.header import inject_theme, render_page_header
from components.sidebar import render_sidebar
from components.search_bar import render_search_bar, render_example_queries
from components.loading_screen import render_loading_screen
from components.error_state import render_error_state
from components.footer import render_footer

st.set_page_config(page_title=f"Search · {config.APP_NAME}", page_icon=config.APP_ICON, layout="wide")

init_session_state()
inject_theme()
render_sidebar()

render_page_header("Search", "Describe what you're looking for, in English, Bengali, or Banglish.")

col1, col2, col3 = st.columns([1, 5, 1])
with col2:
    query, submitted = render_search_bar(key_prefix="search", button_label="Search")
    clicked_example = render_example_queries(key_prefix="search")

    with st.expander("Advanced options", expanded=False):
        a1, a2 = st.columns(2)
        with a1:
            language = st.selectbox(
                "Language",
                options=config.SUPPORTED_LANGUAGES,
                index=config.SUPPORTED_LANGUAGES.index(st.session_state["language"]),
            )
            top_k = st.slider(
                "Top-K results",
                min_value=config.MIN_TOP_K,
                max_value=config.MAX_TOP_K,
                value=st.session_state["top_k"],
            )
        with a2:
            rerank_enabled = st.toggle("Re-ranking (cross-encoder)", value=st.session_state["rerank_enabled"])
            hybrid_enabled = st.toggle("Hybrid search (dense + BM25)", value=st.session_state["hybrid_enabled"])

        st.session_state["language"] = language
        st.session_state["top_k"] = top_k
        st.session_state["rerank_enabled"] = rerank_enabled
        st.session_state["hybrid_enabled"] = hybrid_enabled

    effective_query = clicked_example or (query if submitted else None)

    if effective_query:
        st.session_state["query"] = effective_query
        push_search_history(effective_query)

        loading_placeholder = st.empty()
        with loading_placeholder.container():
            render_loading_screen(f'Searching for "{effective_query}"...')

        try:
            results = search_videos(
                effective_query,
                top_k=st.session_state["top_k"],
                rerank=st.session_state["rerank_enabled"],
                hybrid=st.session_state["hybrid_enabled"],
            )
            set_results(results)
            loading_placeholder.empty()
            st.switch_page("pages/2_Results.py")
        except APIError as e:
            loading_placeholder.empty()
            render_error_state("Search failed", details=str(e))

    st.markdown("<br/>", unsafe_allow_html=True)

    if st.session_state.get("results"):
        st.info(
            f'Showing results for your last search: "{st.session_state["query"]}". '
            "Run a new search above, or view the full results.",
            icon="ℹ️",
        )
        if st.button("View last results →"):
            st.switch_page("pages/2_Results.py")

render_footer()
