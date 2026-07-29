"""
components/transcript_card.py
------------------------------
Renders a styled transcript snippet block with its timestamp.
"""

import streamlit as st


def render_transcript_card(transcript: str, timestamp: str = None):
    st.markdown('<div class="rag-section-label">Transcript Snippet</div>', unsafe_allow_html=True)
    ts_html = f'<span class="rag-badge">⏱ {timestamp}</span>' if timestamp else ""
    st.markdown(
        f"""
        <div class="rag-transcript">{transcript}</div>
        <div style="margin-top:0.5rem;">{ts_html}</div>
        """,
        unsafe_allow_html=True,
    )
