"""
components/sidebar.py
----------------------
Persistent sidebar: branding, navigation, recent searches, recent videos,
theme switch, and a shortcut into Settings.
"""

import streamlit as st

import config
import dummy_data


def render_sidebar():
    with st.sidebar:
        st.markdown(
            f"""
            <div style="display:flex; align-items:center; gap:0.55rem; padding: 0.3rem 0 1.1rem 0;">
                <span style="font-size:1.6rem;">{config.APP_ICON}</span>
                <span style="font-size:1.25rem; font-weight:800;">{config.APP_NAME}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.page_link("app.py", label="Home", icon="🏠")
        st.page_link("pages/1_Search.py", label="Search", icon="🔍")
        st.page_link("pages/2_Results.py", label="Results", icon="📊")
        st.page_link("pages/3_Settings.py", label="Settings", icon="⚙️")
        st.page_link("pages/4_About.py", label="About", icon="ℹ️")

        st.markdown("---")

        st.markdown('<div class="rag-section-label">Recent Searches</div>', unsafe_allow_html=True)
        history = st.session_state.get("search_history") or []
        if history:
            for q in history[:5]:
                if st.button(f"🕐 {q}", key=f"hist_{q}", use_container_width=True):
                    st.session_state["query"] = q
                    st.switch_page("pages/1_Search.py")
        else:
            st.caption("No searches yet this session.")

        st.markdown("---")

        st.markdown('<div class="rag-section-label">Recent Videos</div>', unsafe_allow_html=True)
        recent_videos = dummy_data.get_all_videos()[:3]
        for v in recent_videos:
            if st.button(f"🎬 {v['title']}", key=f"recent_{v['video_id']}", use_container_width=True):
                st.session_state["selected_video"] = v["video_id"]
                st.switch_page("pages/2_Results.py")

        st.markdown("---")

        theme = st.session_state.get("theme", "dark")
        toggle_label = "☀️ Switch to Light" if theme == "dark" else "🌙 Switch to Dark"
        if st.button(toggle_label, use_container_width=True):
            st.session_state["theme"] = "light" if theme == "dark" else "dark"
            st.rerun()

        st.caption(f"Mock mode: {'ON' if config.USE_MOCK_DATA else 'OFF'}")
