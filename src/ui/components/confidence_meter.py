"""
components/confidence_meter.py
-------------------------------
Small horizontal bar used to visualize confidence/similarity scores.
"""

import streamlit as st


def render_confidence_meter(label: str, value: float, is_percent: bool = True):
    """
    label     : e.g. "Confidence" or "Similarity"
    value     : 0-100 if is_percent else 0.0-1.0
    """
    pct = value if is_percent else value * 100
    pct = max(0, min(100, pct))
    display_value = f"{int(pct)}%" if is_percent else f"{value:.2f}"

    st.markdown(
        f"""
        <div style="margin-bottom:0.6rem;">
            <div style="display:flex; justify-content:space-between; font-size:0.85rem;">
                <span class="muted">{label}</span>
                <span style="font-weight:600;">{display_value}</span>
            </div>
            <div class="rag-meter-track">
                <div class="rag-meter-fill" style="width:{pct}%;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
