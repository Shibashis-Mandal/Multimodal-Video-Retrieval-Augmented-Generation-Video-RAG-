"""
components/empty_state.py
--------------------------
Shown when there is no query/result yet (e.g. user opens Results page
directly without searching first).
"""

import streamlit as st


def render_empty_state(
    title: str = "Nothing here yet",
    message: str = "Run a search to see results appear here.",
    icon: str = "🔎",
    cta_label: str = "Go to Search",
    cta_page: str = "pages/1_Search.py",
):
    st.markdown(
        f"""
        <div class="rag-state">
            <div class="icon">{icon}</div>
            <div style="font-weight:700; font-size:1.1rem; color:var(--app-text-primary);">{title}</div>
            <div class="muted">{message}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if cta_label and cta_page:
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if st.button(cta_label, use_container_width=True):
                st.switch_page(cta_page)
