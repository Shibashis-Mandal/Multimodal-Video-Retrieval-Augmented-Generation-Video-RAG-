# RecipeRAG — Video-RAG Frontend

A complete, standalone Streamlit frontend for a Multimodal Video
Retrieval-Augmented Generation system. **No backend required** — everything
runs on realistic mock data today, and is structured so the real backend can
be plugged in later by editing a single file.

```
streamlit run app.py
```

---

## 1. Project Structure

```
video_rag_frontend/
├── app.py                  # Home page (Streamlit entry point)
├── config.py                # All settings/flags/theme colors in one place
├── dummy_data.py             # Fake "database" matching the real API contract
├── requirements.txt
├── pages/                    # Streamlit multipage app pages
│   ├── 1_Search.py
│   ├── 2_Results.py
│   ├── 3_Settings.py
│   └── 4_About.py
├── components/                # Reusable, presentation-only UI building blocks
│   ├── header.py               # theme injection + page headers
│   ├── sidebar.py               # nav, recent searches, recent videos, theme toggle
│   ├── search_bar.py             # search input + example query pills
│   ├── video_card.py              # grid card (top-5 results)
│   ├── result_card.py              # detailed right-panel (summary/ingredients/etc.)
│   ├── video_player.py              # left-panel player + timestamp controls
│   ├── transcript_card.py            # transcript snippet block
│   ├── ingredient_tags.py             # ingredient chip list
│   ├── confidence_meter.py             # confidence/similarity bar
│   ├── loading_screen.py                # "searching..." state
│   ├── empty_state.py                    # "no results yet" state
│   ├── error_state.py                     # API-error state
│   └── footer.py
├── utils/
│   ├── api_client.py           # ⭐ THE SEAM — mock/real backend switch lives here
│   └── session_state.py         # st.session_state schema + init helper
├── styles/
│   └── theme.css                # dark/light theme, ChatGPT/Perplexity-inspired
└── assets/
    └── thumbnails/                # placeholder video thumbnails
```

### Why this structure?

| Folder/File | Purpose |
|---|---|
| `pages/` | Streamlit's built-in multipage convention. Each file is a page; numeric prefixes order them, though navigation itself is handled by our custom sidebar so the default nav is hidden. |
| `components/` | Pure, reusable render functions. No page imports another page's internals — everything shared lives here so it's written once and used everywhere. |
| `utils/api_client.py` | The **only** file that talks to data. Pages/components never import `dummy_data.py` directly or call `requests` themselves — they call `api_client` functions. This is what makes the backend swap a one-file change. |
| `utils/session_state.py` | Prevents "KeyError" bugs from Streamlit's stateless reruns by centralizing what keys exist and their defaults. |
| `config.py` | One flag (`USE_MOCK_DATA`) controls the entire app's data source. Theme colors, defaults, and feature flags also live here instead of being hardcoded in pages. |
| `dummy_data.py` | Isolated from the UI entirely — could be deleted on the day the backend ships with zero impact on `pages/` or `components/`. |
| `styles/theme.css` | One stylesheet, themed via CSS variables set per dark/light mode, instead of inline styles scattered across every page. |

---

## 2. Data Flow

**Today (mock mode):**

```
User → Page (e.g. Search) → utils/api_client.py → dummy_data.py → UI
```

**Once the backend exists:**

```
User → Frontend → REST API → Backend
                                ↓
                          Vector Database
                                ↓
                            Retriever
                                ↓
                            Re-ranker
                                ↓
                               LLM
                                ↓
                          JSON Response
                                ↓
                            Frontend
```

### What changes when the backend is ready

1. Open `config.py` and set:
   ```python
   USE_MOCK_DATA = False
   API_BASE_URL = "https://your-backend-url"
   ```
2. Open `utils/api_client.py`. Each function (`search_videos`, `get_video`,
   `get_metadata`, `get_history`) already has the real `requests` call
   written out and commented directly below the mock branch — uncomment it.
3. Done.

### What does **not** change

- `pages/*.py`
- `components/*.py`
- `styles/theme.css`
- `utils/session_state.py`

None of these files know or care whether data came from `dummy_data.py` or a
live API, because they only ever call functions in `api_client.py` and
consume the same dict shape either way.

---

## 3. API Design (for the future backend)

### `POST /search`

**Request**
```json
{
  "query": "fish curry with mustard paste",
  "top_k": 5,
  "rerank": true,
  "hybrid": true
}
```

**Response `200`**
```json
{
  "query": "fish curry with mustard paste",
  "answer": "Based on your dataset, here is the best match: Shorshe Ilish...",
  "rerank_applied": true,
  "hybrid_applied": true,
  "top_k": 5,
  "results": [
    {
      "video_id": "bengali_recipe_003",
      "title": "Shorshe Ilish (Hilsa in Mustard Gravy)",
      "creator": "member_2",
      "language": "bn",
      "dish_type": "Main Course / Fish",
      "duration": "00:52",
      "duration_sec": 52,
      "video_path": "assets/videos/bengali_recipe_003.mp4",
      "thumbnail": "assets/thumbnails/bengali_recipe_003.jpg",
      "ingredients": ["Hilsa Fish", "Mustard Paste", "Green Chilies"],
      "summary": "Hilsa fish steamed in a pungent mustard paste gravy...",
      "transcript_snippet": "...shorshe bata ta chalan diye niye nao...",
      "timestamp": "00:15",
      "confidence": 92,
      "similarity": 0.88
    }
  ]
}
```

**Errors**
| Status | Meaning |
|---|---|
| `400` | Missing/empty `query` |
| `422` | Invalid `top_k`, `rerank`, or `hybrid` type |
| `500` | Retrieval/re-ranking/LLM pipeline failure |

### `GET /video/{id}`
Returns a single result object (same shape as one item in `results` above).
`404` if `id` doesn't exist.

### `GET /metadata/{id}`
Returns a lighter payload (no `summary`/`transcript_snippet`):
```json
{
  "video_id": "bengali_recipe_003",
  "title": "Shorshe Ilish (Hilsa in Mustard Gravy)",
  "creator": "member_2",
  "language": "bn",
  "dish_type": "Main Course / Fish",
  "duration": "00:52",
  "ingredients": ["Hilsa Fish", "Mustard Paste", "Green Chilies"]
}
```

### `GET /history`
Returns persisted search history for the current user:
```json
[
  {"query": "fish recipe with mustard paste", "timestamp": "2026-07-24T10:15:00"}
]
```

---

## 4. State Management (`st.session_state`)

Streamlit reruns the whole script on every interaction, so anything that
needs to survive a rerun must live in `st.session_state`. This app
centralizes that schema in `utils/session_state.py`:

| Key | Type | Holds |
|---|---|---|
| `query` | `str` | Current/last submitted search query |
| `results` | `dict \| None` | Last response from `api_client.search_videos()` |
| `selected_video` | `str \| None` | `video_id` currently shown in the Results left/right panels |
| `search_history` | `list[str]` | Session-local recent searches (most recent first) |
| `theme` | `"dark" \| "light"` | Active theme |
| `top_k`, `rerank_enabled`, `hybrid_enabled`, `language` | mixed | Advanced search options / user defaults |
| `is_searching` | `bool` | Drives the loading state |

**Rule of thumb used throughout this codebase:** components never read or
write `st.session_state` for keys they don't own — pages own the state,
components receive plain data as function arguments and return plain values
(e.g. `render_search_bar()` returns `(query, submitted)` instead of mutating
state itself). This keeps components testable and reusable outside a
specific page's state assumptions.

---

## 5. Best Practices Used Here

- **UI/logic separation**: `components/` never imports `dummy_data.py` or
  makes network calls — only `api_client.py` does.
- **Single source of truth for data shape**: the dict returned by
  `dummy_data.mock_search()` today is byte-for-byte what the real `/search`
  response will look like, documented once in this README.
- **No duplicated markup**: anything rendered more than once (cards, tags,
  meters, states) is a function in `components/`.
- **Config over hardcoding**: colors, defaults, and the mock/live switch
  live in `config.py`, not scattered through pages.
- **Consistent naming**: `render_*` for components that draw UI,
  `mock_*` for fake-data functions, `get_*`/`search_*` for the
  `api_client` functions that pages actually call.
- **Caching**: `search_videos()` uses `st.cache_data` so repeated identical
  searches within a session don't re-hit the (future) network.
- **Graceful failure**: every `api_client` call can raise `APIError`, and
  every page that calls it wraps the call in `try/except` and renders
  `components/error_state.py` instead of crashing.

---

## 6. Known Placeholders

- `assets/videos/*.mp4` don't exist yet — `components/video_player.py`
  falls back to the thumbnail + an explanatory notice when no video file is
  found at `video_path`. Drop real files in and playback works immediately.
- Thumbnails in `assets/thumbnails/` are generated placeholder images, not
  real video frames.
