# Nafis - L3 Unified Query Engine

This folder contains my Layer 3 contribution for the Multimodal Video-RAG
project.

## Main Files

`06_unified_query_engine.py`

`app.py`

## Purpose

The L3 engine accepts a user query and retrieves the most relevant video using:

- FAISS vector search
- BM25 lexical search
- Knowledge graph lookup
- Answer generation using template, Gemini, or Qwen2.5

## Expected Input Structure

The engine expects an output folder containing:

```text
output/
├── Metadata/
├── FAISS_Index/
└── Knowledge_Graph/
```

## Run

Run the L3 engine directly:

```bash
python 06_unified_query_engine.py --out output --backend template
```

Optional answer backends:

```bash
python 06_unified_query_engine.py --out output --backend gemini
python 06_unified_query_engine.py --out output --backend qwen
```

Run the Streamlit demo UI:

```bash
streamlit run app.py -- --out output --l3-dir .
```

## Notes

The `dataset/` and `output/` folders are placeholders for local testing
artifacts. Large videos, model files, generated indexes, and virtual
environments should not be committed unless the team specifically requires
them.
