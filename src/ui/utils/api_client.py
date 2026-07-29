"""
utils/api_client.py
--------------------
THE SEAM. This is the one and only file that needs to change when the real
backend goes live.

Every page/component in this app calls the functions below instead of
touching `dummy_data.py` or `requests` directly. That means:

  - Today (USE_MOCK_DATA=True):  these functions return `dummy_data.py` output.
  - Tomorrow (USE_MOCK_DATA=False): these functions call the real REST API.

The function signatures and return shapes are FROZEN to match the API design
in README.md, so flipping the switch requires editing only the bodies of the
functions in this file — no page or component code changes.
"""

import time
from typing import Optional

import streamlit as st

import config
import dummy_data

# When USE_MOCK_DATA=False, this is the only extra import you'll need:
# import requests


class APIError(Exception):
    """Raised when the backend returns an error or is unreachable."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


def _simulate_latency():
    if config.MOCK_LATENCY_SECONDS:
        time.sleep(config.MOCK_LATENCY_SECONDS)


@st.cache_data(show_spinner=False, ttl=300)
def search_videos(query: str, top_k: int = 5, rerank: bool = True, hybrid: bool = True):
    """
    Search cooking videos by natural-language query.

    Mock behaviour: delegates to dummy_data.mock_search().

    Real backend swap:
        response = requests.post(
            f"{config.API_BASE_URL}/search",
            json={"query": query, "top_k": top_k, "rerank": rerank, "hybrid": hybrid},
            timeout=15,
        )
        if response.status_code != 200:
            raise APIError(response.text, response.status_code)
        return response.json()

    Returns
    -------
    dict: {
        "query": str,
        "answer": str,               # LLM-synthesized natural language answer
        "rerank_applied": bool,
        "hybrid_applied": bool,
        "top_k": int,
        "results": [
            {
                "video_id": str, "title": str, "creator": str, "language": str,
                "dish_type": str, "duration": str, "duration_sec": int,
                "video_path": str, "thumbnail": str, "ingredients": [str],
                "summary": str, "transcript_snippet": str, "timestamp": str,
                "confidence": int, "similarity": float,
            }, ...
        ],
    }
    """
    if config.USE_MOCK_DATA:
        _simulate_latency()
        return dummy_data.mock_search(query, top_k=top_k, rerank=rerank, hybrid=hybrid)

    # --- Real backend call (uncomment when backend exists) -----------------
    # import requests
    # response = requests.post(
    #     f"{config.API_BASE_URL}/search",
    #     json={"query": query, "top_k": top_k, "rerank": rerank, "hybrid": hybrid},
    #     timeout=15,
    # )
    # if response.status_code != 200:
    #     raise APIError(response.text, response.status_code)
    # return response.json()
    raise APIError("Backend not configured. Set config.USE_MOCK_DATA=True or implement the API.")


def get_video(video_id: str):
    """
    Fetch full details for a single video.

    Real backend swap: GET {API_BASE_URL}/video/{video_id}
    """
    if config.USE_MOCK_DATA:
        _simulate_latency()
        video = dummy_data.mock_get_video(video_id)
        if video is None:
            raise APIError(f"Video '{video_id}' not found", status_code=404)
        return video

    # import requests
    # response = requests.get(f"{config.API_BASE_URL}/video/{video_id}", timeout=10)
    # if response.status_code == 404:
    #     raise APIError("Video not found", status_code=404)
    # if response.status_code != 200:
    #     raise APIError(response.text, response.status_code)
    # return response.json()
    raise APIError("Backend not configured.")


def get_metadata(video_id: str):
    """
    Fetch lightweight metadata for a video (no summary/transcript).

    Real backend swap: GET {API_BASE_URL}/metadata/{video_id}
    """
    if config.USE_MOCK_DATA:
        _simulate_latency()
        meta = dummy_data.mock_get_metadata(video_id)
        if meta is None:
            raise APIError(f"Metadata for '{video_id}' not found", status_code=404)
        return meta

    # import requests
    # response = requests.get(f"{config.API_BASE_URL}/metadata/{video_id}", timeout=10)
    # ...
    raise APIError("Backend not configured.")


def get_history():
    """
    Fetch server-persisted search history for the current user.

    Real backend swap: GET {API_BASE_URL}/history

    Note: this app also keeps a *local* per-session history in
    st.session_state (see utils/session_state.py) so the UI feels
    instant even before this endpoint is wired up.
    """
    if config.USE_MOCK_DATA:
        _simulate_latency()
        return dummy_data.mock_get_history()

    # import requests
    # response = requests.get(f"{config.API_BASE_URL}/history", timeout=10)
    # ...
    raise APIError("Backend not configured.")
