"""
config.py
---------
Single source of truth for app-wide settings.

WHY THIS FILE EXISTS
When the real backend is ready, you flip `USE_MOCK_DATA` to False and set
`API_BASE_URL`. Nothing else in the UI layer needs to change, because every
page/component reads data through `utils/api_client.py`, which reads its
behaviour from here.
"""

import os

# ---------------------------------------------------------------------------
# BACKEND SWITCH
# ---------------------------------------------------------------------------
# True  -> utils/api_client.py returns data from dummy_data.py (no backend needed)
# False -> utils/api_client.py sends real HTTP requests to API_BASE_URL
USE_MOCK_DATA = True

# Base URL of the future FastAPI / Flask backend. Ignored while USE_MOCK_DATA=True.
API_BASE_URL = os.environ.get("VIDEO_RAG_API_URL", "http://localhost:8000")

# Simulated network latency (seconds) so the loading UI can be previewed
# realistically even without a backend. Set to 0 once real APIs are wired up.
MOCK_LATENCY_SECONDS = 0.9

# ---------------------------------------------------------------------------
# APP METADATA
# ---------------------------------------------------------------------------
APP_NAME = "RecipeRAG"
APP_TAGLINE = "Ask your cooking videos anything."
APP_ICON = "🍲"

# ---------------------------------------------------------------------------
# SEARCH DEFAULTS
# ---------------------------------------------------------------------------
DEFAULT_TOP_K = 5
MIN_TOP_K = 1
MAX_TOP_K = 10
DEFAULT_RERANK = True
DEFAULT_HYBRID = True
SUPPORTED_LANGUAGES = ["Auto-detect", "English", "Bengali (বাংলা)", "Banglish"]

EXAMPLE_QUERIES = [
    "Show me a fish recipe that uses mustard paste",
    "I have prawns, coconut milk and green chilies — what can I make?",
    "How do I fry fish so it doesn't stick to the pan?",
    "Jump to the part where mustard oil is added in Kosha Mangsho",
    "Quick vegetarian recipes under 60 seconds",
]

# ---------------------------------------------------------------------------
# THEME
# ---------------------------------------------------------------------------
THEME = {
    "dark": {
        "bg": "#0b0b0f",
        "bg_secondary": "#141419",
        "bg_card": "#1a1a21",
        "border": "#2a2a33",
        "text_primary": "#f2f2f5",
        "text_secondary": "#9a9aa5",
        "accent": "#7c5cff",
        "accent_soft": "#7c5cff26",
        "success": "#3ddc97",
        "warning": "#ffb454",
        "danger": "#ff6767",
    },
    "light": {
        "bg": "#ffffff",
        "bg_secondary": "#f5f5f8",
        "bg_card": "#ffffff",
        "border": "#e4e4ea",
        "text_primary": "#16161a",
        "text_secondary": "#65656f",
        "accent": "#6d4bff",
        "accent_soft": "#6d4bff1a",
        "success": "#1fa971",
        "warning": "#c97b12",
        "danger": "#d84343",
    },
}

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
THUMBNAILS_DIR = os.path.join(ASSETS_DIR, "thumbnails")
STYLES_DIR = os.path.join(os.path.dirname(__file__), "styles")
