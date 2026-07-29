"""
pages/4_About.py
-----------------
Project description, architecture overview, and current-vs-future data
flow, so anyone opening the app (or reviewing the repo) understands what's
mocked today and what plugs in later.
"""

import streamlit as st

import config
from utils.session_state import init_session_state
from components.header import inject_theme, render_page_header
from components.sidebar import render_sidebar
from components.footer import render_footer

st.set_page_config(page_title=f"About · {config.APP_NAME}", page_icon=config.APP_ICON, layout="wide")

init_session_state()
inject_theme()
render_sidebar()

render_page_header("About", "What this system is, and how the frontend fits into the bigger picture.")

col1, col2, col3 = st.columns([1, 4, 1])
with col2:
    st.markdown('<div class="rag-card">', unsafe_allow_html=True)
    st.markdown("#### What is RecipeRAG?")
    st.write(
        "RecipeRAG is the interface for a Multimodal Video Retrieval-Augmented "
        "Generation (Video-RAG) system built on a dataset of short-form Bengali "
        "cooking videos. It lets you ask natural-language questions — by "
        "ingredient, technique, or exact moment — and get back the most "
        "relevant video clips plus an AI-generated answer."
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="rag-card">', unsafe_allow_html=True)
    st.markdown("#### System Architecture (4 Layers)")
    st.markdown(
        """
1. **L1 — Immutable Dataset**: the raw short-form recipe videos + per-video metadata (title, creator, language, ingredients, dish type, duration).
2. **L2 — Hybrid Retrieval & Re-Ranking**: keyframes + audio go through a Video-RAG index (CLIP-style embeddings); transcripts + metadata go through a Text-RAG index (multilingual text embeddings). Both are merged with Reciprocal Rank Fusion, then a cross-encoder re-ranks the merged candidates.
3. **L3 — Natural Language Query Engine**: turns a user's query into embeddings + keywords, runs it through L2, and synthesizes a final answer with an LLM.
4. **L4 — This Frontend**: the minimalist Streamlit interface you're using right now.
        """
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="rag-card">', unsafe_allow_html=True)
    st.markdown("#### Data Flow — Today (mock)")
    st.code("User → Search Page → dummy_data.py (fake JSON) → api_client.py → UI", language="text")

    st.markdown("#### Data Flow — Once the backend exists")
    st.code(
        "User → Frontend → REST API → Backend\n"
        "                              ↓\n"
        "                        Vector Database\n"
        "                              ↓\n"
        "                          Retriever\n"
        "                              ↓\n"
        "                          Re-ranker\n"
        "                              ↓\n"
        "                             LLM\n"
        "                              ↓\n"
        "                        JSON Response\n"
        "                              ↓\n"
        "                          Frontend",
        language="text",
    )
    st.caption(
        "Only `utils/api_client.py` changes when this switch happens — see the "
        "project README for the exact migration steps and API contract."
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="rag-card">', unsafe_allow_html=True)
    st.markdown("#### Tech Stack (planned)")
    t1, t2 = st.columns(2)
    with t1:
        st.markdown(
            "- **Frontend**: Streamlit\n"
            "- **Vector DB**: Qdrant / ChromaDB\n"
            "- **Visual embeddings**: CLIP / OpenCLIP\n"
        )
    with t2:
        st.markdown(
            "- **Text embeddings**: bge-m3\n"
            "- **Re-ranker**: bge-reranker-large\n"
            "- **Synthesis LLM**: GPT-4o-mini / Gemini\n"
        )
    st.markdown("</div>", unsafe_allow_html=True)

render_footer()
