"""
app.py
------
Home page and entry point of the Streamlit multipage app.

Run with:  streamlit run app.py
"""

import streamlit as st

import config
from utils.session_state import init_session_state, push_search_history
from components.header import inject_theme
from components.sidebar import render_sidebar
from components.search_bar import render_search_bar, render_example_queries
from components.footer import render_footer

st.set_page_config(
    page_title=f"{config.APP_NAME} · {config.APP_TAGLINE}",
    page_icon=config.APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session_state()
inject_theme()
render_sidebar()

# --- Hero -------------------------------------------------------------
st.markdown(
    f"""
    <div class="rag-hero">
        <span class="eyebrow">Multimodal Video-RAG</span>
        <h1>{config.APP_NAME}</h1>
        <p class="subtitle">{config.APP_TAGLINE} Search across cooking videos by ingredient,
        technique, or the exact moment something happens on screen.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Search bar ---------------------------------------------------------
col1, col2, col3 = st.columns([1, 5, 1])
with col2:
    query, submitted = render_search_bar(key_prefix="home", button_label="Search")

    clicked_example = render_example_queries(key_prefix="home")

    effective_query = clicked_example or (query if submitted else None)

    if effective_query:
        st.session_state["query"] = effective_query
        push_search_history(effective_query)
        st.switch_page("pages/1_Search.py")

st.markdown("<br/>", unsafe_allow_html=True)

# --- Recent searches (visible on home too, mirrors sidebar) -------------
history = st.session_state.get("search_history") or []
if history:
    col1, col2, col3 = st.columns([1, 5, 1])
    with col2:
        st.markdown('<div class="rag-section-label">Recent Searches</div>', unsafe_allow_html=True)
        chip_cols = st.columns(min(len(history), 5))
        for c, q in zip(chip_cols, history[:5]):
            with c:
                if st.button(q, key=f"home_recent_{q}", use_container_width=True):
                    st.session_state["query"] = q
                    push_search_history(q)
                    st.switch_page("pages/1_Search.py")

st.markdown("<br/><br/>", unsafe_allow_html=True)

# --- Project description --------------------------------------------------
col1, col2, col3 = st.columns([1, 5, 1])
with col2:
    st.markdown('<div class="rag-card">', unsafe_allow_html=True)
    st.markdown("#### About this project")
    st.write(
        f"{config.APP_NAME} is the frontend for a multimodal Video Retrieval-Augmented "
        "Generation system. Under the hood (once connected), it combines visual "
        "search over video keyframes with text search over transcripts and "
        "metadata, merges both with reciprocal rank fusion, re-ranks the "
        "results with a cross-encoder, and synthesizes a natural-language "
        "answer with an LLM."
    )
    st.caption(
        "This frontend currently runs entirely on mock data — no backend "
        "required. See the About page for the full architecture and "
        "integration plan."
    )
    st.markdown("</div>", unsafe_allow_html=True)

render_footer()
