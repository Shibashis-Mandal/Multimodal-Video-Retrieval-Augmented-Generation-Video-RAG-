"""
pages/2_Results.py
-------------------
Two-column results layout:
  LEFT  : video player + timestamp/playback controls + metadata
  RIGHT : AI summary, ingredients, transcript, scores, details
Below   : grid of the top-K retrieved videos (click to make one the
          selected/left-panel video).
"""

import streamlit as st

import config
from utils.session_state import init_session_state
from utils.api_client import get_video, APIError
from components.header import inject_theme, render_page_header
from components.sidebar import render_sidebar
from components.video_player import render_video_player
from components.result_card import render_result_card
from components.video_card import render_video_card
from components.empty_state import render_empty_state
from components.error_state import render_error_state
from components.footer import render_footer

st.set_page_config(page_title=f"Results · {config.APP_NAME}", page_icon=config.APP_ICON, layout="wide")

init_session_state()
inject_theme()
render_sidebar()

results_payload = st.session_state.get("results")

if not results_payload or not results_payload.get("results"):
    render_page_header("Results", "")
    render_empty_state(
        title="No results yet",
        message="Search for a recipe or technique to see reranked matches, "
        "AI summaries, and transcripts here.",
        icon="🍲",
    )
    render_footer()
    st.stop()

render_page_header(
    "Results",
    f'For your query: "{results_payload.get("query", "")}"',
)

if results_payload.get("answer"):
    st.markdown('<div class="rag-card">', unsafe_allow_html=True)
    st.markdown("**🧠 AI Answer**")
    st.write(results_payload["answer"])
    st.markdown("</div>", unsafe_allow_html=True)

selected_id = st.session_state.get("selected_video") or results_payload["results"][0]["video_id"]

try:
    selected_video = get_video(selected_id)
except APIError as e:
    render_error_state("Could not load the selected video", details=str(e))
    selected_video = None

if selected_video:
    left, right = st.columns([3, 2], gap="large")

    with left:
        render_video_player(selected_video)

    with right:
        render_result_card(selected_video)

st.markdown("<br/><hr/>", unsafe_allow_html=True)

st.markdown('<div class="rag-section-label">Top Retrieved Videos</div>', unsafe_allow_html=True)
top_results = results_payload["results"][: config.MAX_TOP_K][:5]

cols = st.columns(len(top_results)) if top_results else []
for col, video in zip(cols, top_results):
    with col:
        if render_video_card(video, key_suffix="results_grid"):
            st.session_state["selected_video"] = video["video_id"]
            st.session_state["_video_start_seconds"] = 0
            st.rerun()

render_footer()
