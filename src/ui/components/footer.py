"""
components/footer.py
---------------------
Small footer shown at the bottom of every page.
"""

import streamlit as st

import config


def render_footer():
    st.markdown("<br/><hr/>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style="text-align:center; padding: 1rem 0;" class="muted">
            {config.APP_NAME} · Multimodal Video-RAG demo frontend · running on mock data
        </div>
        """,
        unsafe_allow_html=True,
    )
