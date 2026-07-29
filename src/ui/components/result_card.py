"""
components/result_card.py
--------------------------
Right-hand detail panel on the Results page: AI summary, ingredients,
transcript, scores, and quick metadata for the currently selected video.
"""

import streamlit as st

from components.confidence_meter import render_confidence_meter
from components.ingredient_tags import render_ingredient_tags
from components.transcript_card import render_transcript_card


def render_result_card(video: dict):
    st.markdown('<div class="rag-section-label">AI Summary</div>', unsafe_allow_html=True)
    st.write(video.get("summary", "No summary available."))

    st.markdown("<br/>", unsafe_allow_html=True)
    render_confidence_meter("Confidence", video.get("confidence", 0), is_percent=True)
    render_confidence_meter("Similarity", video.get("similarity", 0), is_percent=False)

    st.markdown('<div class="rag-section-label">Ingredients</div>', unsafe_allow_html=True)
    render_ingredient_tags(video.get("ingredients", []))

    st.markdown("<br/>", unsafe_allow_html=True)
    render_transcript_card(
        video.get("transcript_snippet", ""), video.get("timestamp")
    )

    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown('<div class="rag-section-label">Details</div>', unsafe_allow_html=True)
    d1, d2 = st.columns(2)
    with d1:
        st.caption("Dish Type")
        st.write(video.get("dish_type", "—"))
        st.caption("Duration")
        st.write(video.get("duration", "—"))
    with d2:
        st.caption("Creator")
        st.write(video.get("creator", "—"))
        st.caption("Language")
        st.write(video.get("language", "—"))
