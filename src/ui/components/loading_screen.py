"""
components/loading_screen.py
-----------------------------
Loading indicator used while a (mock or real) search request is in flight.
"""

import streamlit as st


def render_loading_screen(message: str = "Searching across videos, transcripts, and metadata..."):
    st.markdown(
        f"""
        <div class="rag-state">
            <div class="icon">🍳</div>
            <div style="font-weight:600; color:var(--app-text-primary);">{message}</div>
            <div class="muted">Running hybrid retrieval + re-ranking...</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.progress(100, text=None)
