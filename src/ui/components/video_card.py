"""
components/video_card.py
-------------------------
Compact card used in grids: Top-5 retrieved videos on the Results page,
Recent Videos, etc. Distinct from result_card.py, which renders the
detailed right-hand panel for the single *selected* video.
"""

import os

import streamlit as st


def render_video_card(video: dict, key_suffix: str = ""):
    """Renders one card. Returns True if its "View" button was clicked."""
    with st.container():
        st.markdown('<div class="rag-video-card">', unsafe_allow_html=True)

        thumb = video.get("thumbnail", "")
        if thumb and os.path.exists(thumb):
            st.image(thumb, use_container_width=True)
        else:
            st.markdown(
                '<div class="rag-video-thumb" style="display:flex;align-items:center;'
                'justify-content:center;background:var(--app-bg-secondary);">🎬</div>',
                unsafe_allow_html=True,
            )

        st.markdown('<div class="rag-video-card-body">', unsafe_allow_html=True)
        st.markdown(f'<div class="rag-video-title">{video.get("title", "Untitled")}</div>', unsafe_allow_html=True)

        st.markdown(
            f"""
            <div class="rag-video-meta-row">
                <span>🎯 {video.get('confidence', 0)}%</span>
                <span>📐 {video.get('similarity', 0)}</span>
                <span>⏱ {video.get('duration', '—')}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

        clicked = st.button(
            "View details",
            key=f"view_{video['video_id']}_{key_suffix}",
            use_container_width=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    return clicked
