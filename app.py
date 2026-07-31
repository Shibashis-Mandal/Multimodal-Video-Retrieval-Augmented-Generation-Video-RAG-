"""
L4 — Minimalist UI for the Video-RAG system.

"""
import glob
import importlib.util
import os
import sys
from pathlib import Path

import streamlit as st


# ---------------------------------------------------------------- config ----

def get_arg(flag: str, env_var: str, default: str) -> str:
    if flag in sys.argv:
        return sys.argv[sys.argv.index(flag) + 1]
    return os.environ.get(env_var, default)


OUT_DIR = get_arg("--out", "VIDEO_RAG_OUT_DIR", "final_bundle")
L3_DIR = get_arg("--l3-dir", "VIDEO_RAG_L3_DIR", str(Path(__file__).resolve().parent))

METADATA_DIR = os.path.join(OUT_DIR, "Metadata")
KEYFRAMES_DIR = os.path.join(OUT_DIR, "Keyframes")
AUDIO_DIR = os.path.join(OUT_DIR, "Audio")

st.set_page_config(page_title="ISI Bengali Recipe Video Retrieval System", layout="wide")


# --------------------------------------------------------- load L3 engine ---

def _load_l3_module():
    path = Path(L3_DIR) / "06_unified_query_engine.py"
    if not path.exists():
        st.error(f"Can't find L3 module at {path}. Pass --l3-dir pointing at the folder "
                 f"containing 06_unified_query_engine.py.")
        st.stop()
    spec = importlib.util.spec_from_file_location("unified_query_engine", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@st.cache_resource
def get_engine(answer_backend: str):
    l3 = _load_l3_module()
    return l3.VideoRAGEngine(out_dir=OUT_DIR, answer_backend=answer_backend)


@st.cache_data
def load_all_metadata():
    import json
    records = {}
    for path in sorted(glob.glob(os.path.join(METADATA_DIR, "*.json"))):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        records[data["video_info"]["video_id"]] = data
    return records


# ------------------------------------------------------------------- UI -----

st.title("ISI Bengali Recipe Video Retrieval System")

with st.sidebar:
    st.markdown(f"**Data folder:** `{OUT_DIR}`")
    st.markdown(f"**L3 module:** `{L3_DIR}/06_unified_query_engine.py`")
    all_meta = load_all_metadata()
    st.markdown(f"**Videos indexed:** {len(all_meta)}")
    if all_meta:
        st.caption(", ".join(sorted(all_meta.keys())))
    backend_choice = st.selectbox("Answer backend", ["template", "gemini", "qwen"],
                                   format_func=lambda x: {"template": "Template (no LLM)",
                                                           "gemini": "Gemini API",
                                                           "qwen": "Qwen2.5 (local GPU)"}[x])
    videos_folder_override = st.text_input("Local videos folder (optional, for playback)", value="")
    top_k = st.slider("Results per channel", 1, 10, 3)

query = st.text_input("Search in Bengali, Banglish, or English",
                       placeholder="e.g. How do I make doi katla? / I have prawns and coconut milk...")
go = st.button("Search", type="primary")

if go and query.strip():
    with st.spinner("Loading L3 engine and searching (Vector + Lexical + Knowledge Graph)..."):
        try:
            engine = get_engine(backend_choice)
        except Exception as e:
            st.error(f"Failed to load L3 engine: {e}")
            st.stop()
        result = engine.answer(query, top_k=top_k)

    top_video_id = result["top_video_id"]
    top_timestamp = result["top_timestamp"]
    top_score = result["top_score"]

    left, right = st.columns([1, 1])

    with left:
        st.subheader("Matched clip")
        if top_video_id and top_video_id in all_meta:
            meta = all_meta[top_video_id]
            video_path = meta["video_info"].get("video_path", "")
            local_candidate = None
            if videos_folder_override:
                local_candidate = os.path.join(videos_folder_override, meta["video_info"]["video_name"])

            if local_candidate and os.path.exists(local_candidate):
                st.video(local_candidate, start_time=int(top_timestamp))
            elif os.path.exists(video_path):
                st.video(video_path, start_time=int(top_timestamp))
            else:
                st.info("Original video file not found locally — showing keyframe + audio instead. "
                        "Set 'Local videos folder' in the sidebar to enable full playback.")
                kf_dir = os.path.join(KEYFRAMES_DIR, top_video_id)
                kf_files = sorted(glob.glob(os.path.join(kf_dir, "*.jpg")))
                if kf_files:
                    st.image(kf_files[len(kf_files) // 2], caption=f"{top_video_id} (representative frame)")
                audio_path = os.path.join(AUDIO_DIR, f"{top_video_id}.wav")
                if os.path.exists(audio_path):
                    st.audio(audio_path)
            st.caption(f"Timestamp: {top_timestamp:.2f}s" if top_timestamp else "")
        else:
            st.info("No matching video found.")

    with right:
        st.subheader("Answer")
        st.write(result["answer"])
        st.caption(f"Answer backend: {result['answer_backend']}")

        if top_score is not None:
            confidence_pct = max(0.0, min(top_score, 1.0)) * 100
            st.metric("Relevance", f"{confidence_pct:.0f}%")

        if top_video_id and top_video_id in all_meta:
            meta = all_meta[top_video_id]
            recipe = meta.get("recipe_information", {})
            l3 = _load_l3_module()
            ingredients = l3.extract_string_list(recipe.get("ingredients", []))
            if ingredients:
                st.markdown("**Ingredients**")
                st.write(", ".join(ingredients))

            transcript = meta.get("audio_information", {}).get("transcript_en", "") or \
                         meta.get("audio_information", {}).get("transcript_bn", "")
            if transcript:
                st.markdown("**Transcript snippet**")
                st.caption(transcript[:400] + ("..." if len(transcript) > 400 else ""))

        with st.expander("Show retrieved context (debug)"):
            st.text(result["context_str"] if result["context_str"] else "No context retrieved.")

elif go:
    st.warning("Enter a query first.")
