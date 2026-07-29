"""
dummy_data.py
-------------
Fake "database" that stands in for the real backend (Vector DB + Re-ranker +
LLM synthesis, per the Video-RAG architecture doc).

WHY THIS FILE EXISTS
Every field here matches the JSON contract the real backend is expected to
return (see README.md -> API Design). Keeping the shape identical means that
the day the backend exists, `utils/api_client.py` can swap this module out
for `requests.post(...)` calls and nothing downstream (pages/components)
needs to change.

Do NOT put any Streamlit calls in this file — it must stay pure data/logic,
importable by both the UI and, later, by real backend tests.
"""

from datetime import datetime, timedelta
import random

VIDEOS = [
    {
        "video_id": "bengali_recipe_001",
        "title": "Kosha Mangsho (60s Quick Recipe)",
        "creator": "member_3",
        "language": "bn",
        "dish_type": "Main Course / Non-Veg",
        "duration": "00:58",
        "duration_sec": 58,
        "video_path": "assets/videos/bengali_recipe_001.mp4",
        "thumbnail": "assets/thumbnails/bengali_recipe_001.jpg",
        "ingredients": ["Mutton", "Mustard Oil", "Onions", "Yogurt", "Garam Masala"],
        "summary": (
            "A rich, slow-cooked mutton curry. Onions are caramelized in "
            "mustard oil, mutton is seared, then simmered with yogurt and "
            "garam masala until the gravy clings to the meat."
        ),
        "transcript_snippet": (
            "...ekhon moshla ta bhalo kore koshate hobe, jotokkhon na tel "
            "chere ase... [now the spices need to be cooked well until the "
            "oil separates]"
        ),
        "timestamp": "00:18",
        "confidence": 96,
        "similarity": 0.91,
    },
    {
        "video_id": "bengali_recipe_002",
        "title": "Chingri Malaikari",
        "creator": "member_1",
        "language": "bn",
        "dish_type": "Main Course / Seafood",
        "duration": "00:55",
        "duration_sec": 55,
        "video_path": "assets/videos/bengali_recipe_002.mp4",
        "thumbnail": "assets/thumbnails/bengali_recipe_002.jpg",
        "ingredients": ["Prawns", "Coconut Milk", "Green Chilies", "Bay Leaf", "Ginger Paste"],
        "summary": (
            "Jumbo prawns simmered gently in a fragrant coconut milk gravy "
            "with green chilies and warm spices — a Bengali festive classic."
        ),
        "transcript_snippet": (
            "...narkel dudh ta dhire dhire dite hobe, noile phete jete pare... "
            "[add the coconut milk slowly, or it may curdle]"
        ),
        "timestamp": "00:22",
        "confidence": 94,
        "similarity": 0.89,
    },
    {
        "video_id": "bengali_recipe_006",
        "title": "Cholar Dal (Bengal Gram Lentils)",
        "creator": "member_2",
        "language": "bn",
        "dish_type": "Side / Vegetarian",
        "duration": "00:50",
        "duration_sec": 50,
        "video_path": "assets/videos/bengali_recipe_006.mp4",
        "thumbnail": "assets/thumbnails/bengali_recipe_006.jpg",
        "ingredients": ["Bengal Gram", "Coconut Slices", "Bay Leaf", "Cumin", "Ghee"],
        "summary": (
            "Sweet-and-savory split chickpea lentils, finished with fried "
            "coconut slices and a ghee tempering — a festive Bengali staple."
        ),
        "transcript_snippet": (
            "...narkel ta halka bhaja hole dal e dite hobe... "
            "[once the coconut is lightly fried, add it to the dal]"
        ),
        "timestamp": "00:35",
        "confidence": 81,
        "similarity": 0.77,
    },
  
    
]


def _now_minus(days=0, hours=0, minutes=0):
    return (datetime.now() - timedelta(days=days, hours=hours, minutes=minutes)).isoformat()


# Seed data for "recent searches" / "search history" shown before any real
# query has been made in this session.
SEED_SEARCH_HISTORY = [
    {"query": "fish recipe with mustard paste", "timestamp": _now_minus(hours=2)},
    {"query": "quick prawn curry", "timestamp": _now_minus(days=1)},
    {"query": "vegetarian breakfast under a minute", "timestamp": _now_minus(days=2)},
]


def get_all_videos():
    """Return the full mock video catalogue."""
    return VIDEOS


def mock_search(query: str, top_k: int = 5, rerank: bool = True, hybrid: bool = True):
    """
    Simulate what POST /search will return from the real backend.

    Real backend behaviour this stands in for:
      1. Dense vector search on Visual + Text indices (top-20 each)
      2. BM25 keyword search over ingredients/transcripts
      3. Reciprocal Rank Fusion merge
      4. Cross-encoder re-ranking -> final sorted list
      5. LLM synthesis of a natural-language answer

    Returns a dict matching the exact contract documented in
    README.md -> "POST /search" response schema.
    """
    if not query or not query.strip():
        return {"query": query, "answer": "", "results": []}

    # Deterministic-ish "relevance" shuffle seeded by the query string so the
    # same query always returns the same mock ordering (nice for demos).
    rng = random.Random(query.lower().strip())
    pool = VIDEOS.copy()
    rng.shuffle(pool)

    results = pool[: max(1, min(top_k, len(pool)))]

    # Slightly perturb confidence/similarity per query so results don't look
    # static across different searches.
    perturbed = []
    for v in results:
        item = v.copy()
        jitter = rng.randint(-4, 4)
        item["confidence"] = max(50, min(99, item["confidence"] + jitter))
        item["similarity"] = round(max(0.5, min(0.99, item["similarity"] + jitter / 100)), 2)
        perturbed.append(item)

    perturbed.sort(key=lambda v: v["confidence"], reverse=True)

    top = perturbed[0]
    answer = (
        f"Based on your dataset, here is the best match: **{top['title']}**. "
        f"You can jump to {top['timestamp']} in the video to see the key step."
    )

    return {
        "query": query,
        "answer": answer,
        "rerank_applied": rerank,
        "hybrid_applied": hybrid,
        "top_k": top_k,
        "results": perturbed,
    }


def mock_get_video(video_id: str):
    """Simulate GET /video/{id}."""
    for v in VIDEOS:
        if v["video_id"] == video_id:
            return v
    return None


def mock_get_metadata(video_id: str):
    """Simulate GET /metadata/{id} — a lighter payload than the full video record."""
    v = mock_get_video(video_id)
    if not v:
        return None
    return {
        "video_id": v["video_id"],
        "title": v["title"],
        "creator": v["creator"],
        "language": v["language"],
        "dish_type": v["dish_type"],
        "duration": v["duration"],
        "ingredients": v["ingredients"],
    }


def mock_get_history():
    """Simulate GET /history."""
    return SEED_SEARCH_HISTORY
