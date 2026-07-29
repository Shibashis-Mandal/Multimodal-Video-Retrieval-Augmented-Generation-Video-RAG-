"""
components/video_player.py
---------------------------
Left-panel video player for the Results page. Uses st.video where a real
video file path exists; falls back to a styled placeholder poster since the
dummy dataset doesn't ship actual .mp4 files.

Includes "jump to timestamp" controls that, with a real backend/video file,
would seek the player (st.video supports a `start_time` parameter).
"""

import os

import streamlit as st

import config


def _seconds_from_timestamp(ts: str) -> int:
    try:
        parts = [int(p) for p in ts.split(":")]
        while len(parts) < 3:
            parts.insert(0, 0)
        h, m, s = parts[-3:]
        return h * 3600 + m * 60 + s
    except Exception:
        return 0


def render_video_player(video: dict):
    video_path = video.get("video_path", "")
    thumbnail_path = video.get("thumbnail", "")
    start_at = st.session_state.get("_video_start_seconds", 0)

    if video_path and os.path.exists(video_path):
        st.video(video_path, start_time=start_at)
    else:
        # No real video file yet -> show poster + explanation, still fully functional UI.
        if thumbnail_path and os.path.exists(thumbnail_path):
            st.image(thumbnail_path, use_container_width=True)
        st.info(
            "🎬 Video playback will appear here once real video files are connected. "
            "This is a placeholder poster from the mock dataset.",
            icon="🎬",
        )

    st.markdown(f"**{video.get('title', 'Untitled')}**")
    st.caption(
        f"{video.get('creator', 'unknown')} · {video.get('dish_type', '—')} · "
        f"{video.get('duration', '—')} · lang: {video.get('language', '—')}"
    )

    st.markdown('<div class="rag-section-label">Playback Controls</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("▶️ Play", use_container_width=True, key=f"play_{video['video_id']}"):
            st.toast("Play (wire this to the real player once video files exist).")
    with c2:
        if st.button("⏸️ Pause", use_container_width=True, key=f"pause_{video['video_id']}"):
            st.toast("Pause (wire this to the real player once video files exist).")
    with c3:
        if st.button("⏮️ Restart", use_container_width=True, key=f"restart_{video['video_id']}"):
            st.session_state["_video_start_seconds"] = 0
            st.rerun()
    with c4:
        jump_ts = video.get("timestamp", "00:00")
        if st.button(f"⏭️ Jump to {jump_ts}", use_container_width=True, key=f"jump_{video['video_id']}"):
            st.session_state["_video_start_seconds"] = _seconds_from_timestamp(jump_ts)
            st.rerun()
