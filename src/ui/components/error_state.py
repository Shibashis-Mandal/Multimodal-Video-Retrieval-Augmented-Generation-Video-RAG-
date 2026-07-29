"""
components/error_state.py
--------------------------
Shown when api_client raises an APIError (e.g. real backend unreachable,
video not found).
"""

import streamlit as st


def render_error_state(message: str = "Something went wrong.", details: str = None):
    st.markdown(
        f"""
        <div class="rag-state">
            <div class="icon">⚠️</div>
            <div style="font-weight:700; font-size:1.1rem; color:var(--app-danger);">{message}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if details:
        with st.expander("Error details"):
            st.code(details)
