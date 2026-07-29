"""
components/ingredient_tags.py
------------------------------
Renders a list of ingredients as rounded chip/tag elements.
"""

import streamlit as st


def render_ingredient_tags(ingredients: list):
    if not ingredients:
        st.caption("No ingredients extracted.")
        return
    tags_html = "".join(f'<span class="rag-tag">{ing}</span>' for ing in ingredients)
    st.markdown(f"<div>{tags_html}</div>", unsafe_allow_html=True)
