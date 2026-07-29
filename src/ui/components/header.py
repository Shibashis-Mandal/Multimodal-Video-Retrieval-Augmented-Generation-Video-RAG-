"""
components/header.py
---------------------
Injects the global stylesheet + per-theme CSS variables, and renders the
optional top header bar used on inner pages.
"""

import streamlit as st

import config
from utils.session_state import get_theme_colors


def inject_theme():
    """Load theme.css and bind CSS variables for the active theme.

    Call this once near the top of every page, after init_session_state().
    """
    colors = get_theme_colors()

    with open(f"{config.STYLES_DIR}/theme.css", "r", encoding="utf-8") as f:
        css = f.read()

    variables = f"""
    <style>
    :root {{
        --app-bg: {colors['bg']};
        --app-bg-secondary: {colors['bg_secondary']};
        --app-bg-card: {colors['bg_card']};
        --app-border: {colors['border']};
        --app-text-primary: {colors['text_primary']};
        --app-text-secondary: {colors['text_secondary']};
        --app-accent: {colors['accent']};
        --app-accent-soft: {colors['accent_soft']};
        --app-success: {colors['success']};
        --app-warning: {colors['warning']};
        --app-danger: {colors['danger']};
    }}
    {css}
    </style>
    """
    st.markdown(variables, unsafe_allow_html=True)


def render_page_header(title: str, subtitle: str = ""):
    """Small header used at the top of inner pages (Search, Results, etc.)."""
    st.markdown(
        f"""
        <div style="padding: 0.5rem 0 1.2rem 0;">
            <h2 style="margin-bottom:0.15rem;">{title}</h2>
            <p class="muted" style="margin-top:0;">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
