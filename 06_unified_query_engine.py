"""
Step 5 (L3) — Unified Multi-Channel Query Engine.

This is the ACTUAL L3 layer for the primary pipeline: a standalone,
importable module that does retrieval (Vector/FAISS + Lexical/BM25 +
Structural/Knowledge-Graph) and answer generation, independent of any UI.

Why this file exists separately from 04_query_engine.py and app.py (L4):
  - 04_query_engine.py only does FAISS vector search + generation — it's
    the isi-t5 version of L3, kept for backward compatibility.
  - The tri-channel logic (Vector+BM25+KG) that isi-t6-final introduced
    was previously only living inline inside the L4 Streamlit app, which
    breaks the layer separation — L4 should CALL L3, not contain it.
  - This file is the single source of truth for tri-channel retrieval.
    app.py (L4) imports VideoRAGEngine from here instead of reimplementing
    the search functions itself, so L3 and L4 can't drift out of sync.

Usage (library):
    engine = VideoRAGEngine(out_dir="my_output")
    result = engine.answer("How do I make doi katla?")

Usage (CLI, for testing L3 on its own without the UI):
    python 06_unified_query_engine.py --out my_output
"""
import argparse
import glob
import json
import os
import re


def extract_string_list(items) -> list:
    """Flattens recipe_information['ingredients'] / ['estimated_steps']
    regardless of shape. Confirmed on real data that this field comes back
    in at least 3 different shapes depending on how the Step 2 LLM
    structured its output:
      - flat list of strings: ["Mutton", "Mustard Oil", ...]
      - nested dict of categories: {"marinade": [...], "cooking": [...]}
      - list of {"name": ..., "quantity": ...} dicts: [{"name": "Basmati Rice", "quantity": "1 cup"}, ...]
    The original chunking code (', '.join(...)) only handled the first
    shape correctly and silently dropped data on the other two. This
    recursively flattens all three without losing anything.
    """
    extracted = []
    if isinstance(items, dict):
        for v in items.values():
            extracted.extend(extract_string_list(v))
    elif isinstance(items, list):
        for item in items:
            if isinstance(item, (dict, list)):
                extracted.extend(extract_string_list(item))
            elif item:
                extracted.append(str(item))
    elif isinstance(items, str) and items.strip():
        extracted.append(items)
    return extracted


def tokenize_text(text: str) -> list:
    if not text:
        return []
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    return text.split()


class VideoRAGEngine:
    """Loads L1+L2 artifacts once, then serves queries across all 3 channels."""

    def __init__(self, out_dir: str, answer_backend: str = "template",
                 text_llm_id: str = "Qwen/Qwen2.5-1.5B-Instruct"):
        self.out_dir = out_dir
        self.metadata_dir = os.path.join(out_dir, "Metadata")
        self.faiss_dir = os.path.join(out_dir, "FAISS_Index")
        self.kg_dir = os.path.join(out_dir, "Knowledge_Graph")
        self.answer_backend = answer_backend

        self.all_metadata = self._load_all_metadata()
        self.embedder, self.faiss_index, self.faiss_chunks = self._load_faiss()
        self.bm25_index, self.bm25_refs = self._load_bm25()
        self.kg = self._load_kg()

        self._qwen_tok = None
        self._qwen_model = None
        if answer_backend == "qwen":
            import torch
            from transformers import AutoTokenizer, AutoModelForCausalLM
            self._qwen_tok = AutoTokenizer.from_pretrained(text_llm_id, token=os.environ.get("HF_TOKEN"))
            self._qwen_model = AutoModelForCausalLM.from_pretrained(
                text_llm_id, torch_dtype=torch.float16, device_map="auto", token=os.environ.get("HF_TOKEN"))

    # ---------------------------------------------------------- loading ----

    def _load_all_metadata(self) -> dict:
        records = {}
        for path in sorted(glob.glob(os.path.join(self.metadata_dir, "*.json"))):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            records[data["video_info"]["video_id"]] = data
        return records

    def _load_faiss(self):
        index_file = os.path.join(self.faiss_dir, "video_rag.index")
        chunks_file = os.path.join(self.faiss_dir, "chunks_metadata.json")
        if not os.path.exists(index_file):
            return None, None, None
        try:
            import faiss
            from sentence_transformers import SentenceTransformer
            embedder = SentenceTransformer("all-MiniLM-L6-v2")
            index = faiss.read_index(index_file)
            with open(chunks_file, "r", encoding="utf-8") as f:
                chunks = json.load(f)
            return embedder, index, chunks
        except Exception as e:
            print(f"[WARNING] Vector search unavailable ({e}). Falling back to BM25+KG only.")
            return None, None, None

    def _load_bm25(self):
        from rank_bm25 import BM25Okapi
        corpus, refs = [], []
        for data in self.all_metadata.values():
            video_info = data.get("video_info", {})
            title = video_info.get("title", video_info.get("video_id", ""))
            audio = data.get("audio_information", {})
            transcript = f"{audio.get('transcript_en', '')} {audio.get('transcript_bn', '')}".strip()
            recipe = data.get("recipe_information", {})
            ingredients = " ".join(extract_string_list(recipe.get("ingredients", [])))
            steps = " ".join(extract_string_list(recipe.get("estimated_steps", [])))
            dish = recipe.get("dish_type", "")
            visual_texts = []
            for v in data.get("visual_descriptions", []):
                if v.get("description"):
                    visual_texts.append(v["description"])
                if v.get("ocr_text"):
                    visual_texts.append(v["ocr_text"])
            full_text = f"{title} {dish} {ingredients} {steps} {transcript} {' '.join(visual_texts)}".strip()
            tokens = tokenize_text(full_text)
            if tokens:
                corpus.append(tokens)
                refs.append({"video_id": video_info.get("video_id"), "title": title, "dish": dish,
                             "full_text": full_text, "token_set": set(tokens)})
        if not corpus:
            return None, []
        return BM25Okapi(corpus), refs

    def _load_kg(self):
        import networkx as nx
        graphml_path = os.path.join(self.kg_dir, "video_rag_kg.graphml")
        if not os.path.exists(graphml_path):
            return None
        return nx.read_graphml(graphml_path)

    # --------------------------------------------------------- searching ----

    def search_vector(self, query: str, top_k: int = 5) -> list:
        if self.embedder is None:
            return []
        import faiss
        qvec = self.embedder.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(qvec)
        distances, indices = self.faiss_index.search(qvec, top_k)
        results = []
        for rank, idx in enumerate(indices[0]):
            if 0 <= idx < len(self.faiss_chunks):
                c = dict(self.faiss_chunks[idx])
                c["score"] = float(distances[0][rank])
                results.append(c)
        return results

    def search_bm25(self, query: str, top_k: int = 5) -> list:
        if self.bm25_index is None:
            return []
        tokens = tokenize_text(query)
        if not tokens:
            return []
        query_set = set(tokens)
        scores = self.bm25_index.get_scores(tokens)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        return [{**self.bm25_refs[i], "score": float(scores[i])}
                for i in top_indices if scores[i] > 0 and query_set.intersection(self.bm25_refs[i]["token_set"])]

    def search_kg(self, entities: list) -> list:
        if self.kg is None or not entities:
            return []
        triples = []
        for entity in entities:
            clean = str(entity).strip().lower()
            if not clean:
                continue
            for node in [n for n in self.kg.nodes() if clean in str(n).lower()]:
                for target in self.kg.successors(node):
                    rel = (self.kg.get_edge_data(node, target) or {}).get("relation", "RELATED_TO")
                    triples.append((node, rel, target))
                for source in self.kg.predecessors(node):
                    rel = (self.kg.get_edge_data(source, node) or {}).get("relation", "RELATED_TO")
                    triples.append((source, rel, node))
        return list(set(triples))

    @staticmethod
    def guess_entities(query: str) -> list:
        return [w.capitalize() for w in query.split() if len(w) > 3]

    # ------------------------------------------------------- generation ----

    def _generate(self, query: str, context_str: str) -> tuple:
        system_prompt = (
            "You are an expert culinary AI assistant powered by a Multi-Modal Video RAG system. "
            "Answer the user's question concisely and comprehensively using ONLY the provided context "
            "(semantic, lexical, and knowledge-graph). Do NOT introduce ingredients or facts not in the "
            "context. Cite the video title when relevant."
        )

        if self.answer_backend == "qwen" and self._qwen_model is not None:
            import torch
            messages = [{"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Context:\n{context_str}\n\nQuestion: {query}"}]
            prompt = self._qwen_tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            inputs = self._qwen_tok([prompt], return_tensors="pt").to(self._qwen_model.device)
            with torch.no_grad():
                out = self._qwen_model.generate(**inputs, max_new_tokens=512, repetition_penalty=1.15, do_sample=False)
            answer = self._qwen_tok.decode(out[0][inputs.input_ids.shape[1]:], skip_special_tokens=True).strip()
            return answer, "qwen2.5-local"

        if self.answer_backend == "gemini":
            api_key = os.environ.get("GOOGLE_API_KEY")
            if api_key:
                try:
                    from google import genai
                    client = genai.Client(api_key=api_key)
                    prompt = f"{system_prompt}\n\nContext:\n{context_str}\n\nQuestion: {query}"
                    resp = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
                    return resp.text.strip(), "gemini"
                except Exception as e:
                    return f"(Gemini call failed: {e})", "fallback_template"

        first_block = context_str.split("\n\n=========================================\n\n")[0]
        return f"(No LLM configured — showing top retrieved context directly)\n\n{first_block[:600]}", "template"

    # ------------------------------------------------------- public API ----

    def answer(self, query: str, top_k: int = 5) -> dict:
        """The single entry point L4 (or anything else) should call."""
        vector_hits = self.search_vector(query, top_k=top_k)
        bm25_hits = self.search_bm25(query, top_k=top_k)
        kg_hits = self.search_kg(self.guess_entities(query))

        context_blocks = []
        if vector_hits:
            context_blocks.append("--- SEMANTIC CONTEXT (Vector Search) ---\n" +
                                   "\n\n".join(f"[{h.get('video_title', h.get('video_id'))}] {h['text']}" for h in vector_hits))
        if bm25_hits:
            context_blocks.append("--- KEYWORD CONTEXT (BM25 Lexical) ---\n" +
                                   "\n\n".join(f"[{h['title']} ({h['dish']})] {h['full_text'][:300]}..." for h in bm25_hits))
        if kg_hits:
            context_blocks.append("--- KNOWLEDGE GRAPH TRIPLES ---\n" +
                                   "\n".join(f"({s}) --[{r}]--> ({t})" for s, r, t in kg_hits))
        context_str = "\n\n=========================================\n\n".join(context_blocks)

        answer_text, backend_used = self._generate(query, context_str)

        top_video_id, top_timestamp, top_score = None, 0.0, None
        if vector_hits:
            top_video_id = vector_hits[0].get("video_id")
            top_score = vector_hits[0].get("score")
            if vector_hits[0].get("source") == "visual_frame" and "frame_id" in vector_hits[0]:
                meta = self.all_metadata.get(top_video_id, {})
                frame = next((f for f in meta.get("frame_information", [])
                              if f.get("frame_id") == vector_hits[0]["frame_id"]), None)
                if frame:
                    top_timestamp = frame.get("timestamp", 0.0)
        elif bm25_hits:
            top_video_id = bm25_hits[0].get("video_id")
            top_score = bm25_hits[0].get("score")

        return {
            "query": query,
            "answer": answer_text,
            "answer_backend": backend_used,
            "top_video_id": top_video_id,
            "top_timestamp": top_timestamp,
            "top_score": top_score,
            "vector_hits": vector_hits,
            "bm25_hits": bm25_hits,
            "kg_hits": kg_hits,
            "context_str": context_str,
        }


def main():
    parser = argparse.ArgumentParser(description="L3: tri-channel query engine (CLI, for testing without the UI).")
    parser.add_argument("--out", required=True)
    parser.add_argument("--backend", choices=["template", "gemini", "qwen"], default="template")
    args = parser.parse_args()

    engine = VideoRAGEngine(out_dir=args.out, answer_backend=args.backend)
    print(f"\nL3 engine ready. Videos indexed: {list(engine.all_metadata.keys())}\n")

    while True:
        query = input("Ask a question (or 'exit'): ").strip()
        if query.lower() == "exit":
            break
        result = engine.answer(query)
        print(f"\n[top video: {result['top_video_id']} | score: {result['top_score']} | backend: {result['answer_backend']}]")
        print(result["answer"])
        print()


if __name__ == "__main__":
    main()
