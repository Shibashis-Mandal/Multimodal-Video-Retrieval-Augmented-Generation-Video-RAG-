# Multi-Modal Video RAG Pipeline Architecture

An end-to-end Multi-Modal Retrieval-Augmented Generation (RAG) system designed to ingest, process, index, and query unstructured video content (specifically tailored for instructional and culinary media).

---

# Technical Overview

This repository implements a four-stage Multi-Modal Video RAG Pipeline:

```text
[ Unstructured Video Input ]
            │
            ├─► Audio Extraction ──► Sarvam AI STT (saaras:v3) ──► Bengali & English Transcripts
            │
            ├─► Adaptive Scene Detect ──► Midpoint Keyframe Extraction
            │                                  │
            │                                  ├─► EasyOCR + CLAHE ──► Subtitle Text
            │                                  ├─► YOLOv8 ───────────► Utensil/Object Bounding Boxes
            │                                  └─► Qwen2-VL-2B ──────► Visual Scene Captions
            │
            ▼
[ Qwen2.5-1.5B Structuring ] ──► JSON Metadata Schema
            │
            ├─► Dense Vector Indexing (FAISS + MiniLM-L6-v2)
            ├─► Sparse Lexical Indexing (BM25Okapi)
            └─► Knowledge Graph Construction (NetworkX -> GraphML)
```

---

# Multi-Modal Data Ingestion & Signal Extraction

## Scene Segmentation

- Shot boundary detection via PySceneDetect (AdaptiveDetector) with fallback uniform interval sampling (4s) for sparse visual transitions.

## Auditory Signal Processing

- Audio extraction (pcm_s16le, 16kHz) via FFmpeg.
- Chunked Speech-to-Text (STT) and translation using Sarvam AI (saaras:v3) for bilingual audio processing (Bengali bn-IN and English en-IN) with word-level alignment.

## Visual Signal Processing

- Spatial detection of kitchen utensils and objects via YOLOv8 (yolov8n).
- Bilingual on-screen text extraction using EasyOCR combined with CLAHE (Contrast Limited Adaptive Histogram Equalization) preprocessing and regex noise filtering.
- Action and scene captioning using Qwen2-VL-2B-Instruct in fp16.

---

# Structured Knowledge Modeling

- Assembly of extraction outputs into validated JSON metadata schema.
- Grounded context synthesis using Qwen2.5-1.5B-Instruct for schema-enforced recipe parsing (dish_type, ingredients, estimated_steps, tips, cuisine, tags).
- Directed Knowledge Graph generation via NetworkX, capturing entities (Dish, Cuisine, Ingredient, Step, Utensil/Object) and semantic relations (BELONGS_TO_CUISINE, REQUIRES_INGREDIENT, HAS_STEP, VISUALLY_CONTAINS).
- Exports to GraphML and renders static visualization artifacts via Matplotlib.

---

# Hybrid Retrieval Mechanics

## Dense Semantic Channel

- Text chunking tagged with source metadata (transcript_en, transcript_bn, recipe_info, visual_frame), encoded using SentenceTransformers (all-MiniLM-L6-v2) into 384-dimensional $L_2$-normalized dense vectors, indexed via an inner-product FAISS index (IndexFlatIP).

## Sparse Lexical Channel

- In-memory BM25Okapi index built over tokenized document representations for term-frequency and inverse-document-frequency ($TF$-$IDF$) matching.

## Relational Traversal Channel

- GraphML graph queries for 1-hop and 2-hop relational context expansion.

---

# Repository Structure

```text
.
├── Metadata/                  # JSON metadata output per video
├── Keyframes/                 # Saved keyframes per video shot boundary
├── Audio/                     # Extracted 16kHz mono WAV audio chunks
├── FAISS_Index/
│   ├── video_rag.index        # Serialized FAISS vector index
│   └── chunks_metadata.json   # Chunk definitions and source mappings
├── Knowledge_Graph/
│   ├── video_rag_kg.graphml   # NetworkX directed graph in GraphML format
│   └── knowledge_graph.png    # High-resolution rendering of the Knowledge Graph
├── notebook.ipynb             # Execution notebook
└── README.md                  # System documentation
```

---

# Dependencies & Requirements

## System Prerequisites

- **OS:** Linux / Ubuntu (Kaggle or CUDA-enabled runtime recommended)
- **GPU:** NVIDIA GPU with CUDA support (T4 / P100 / V100 / A100)
- **External Binaries:** ffmpeg, ffprobe

## Python Version

- Python 3.10+ (Tested on Python 3.12.13)

## Python Dependencies

```bash
pip install scenedetect ultralytics easyocr transformers accelerate \
            qwen-vl-utils "pillow<12.0" opencv-python-headless faiss-gpu \
            sentence-transformers requests networkx matplotlib rank-bm25
```
---

# Pipeline Pipeline Stages

## Step 1: Pre-Processing, Audio Transcription & Shot Segmentation

- Extracts audio tracks to PCM 16kHz mono format.
- Splits audio into 25-second chunks and invokes Sarvam AI ASR API (saaras:v3) for Bengali transcription and formal English translation.
- Computes scene boundaries with PySceneDetect and isolates midpoint keyframes.
- Executes yolov8n to extract object bounding boxes and spatial label data.
- Stores output structures in `Metadata/<video_id>_metadata.json`.

---

## Step 2: Multi-Modal Context Extraction & Schema Structuring

- Enhances visual keyframes with Contrast Limited Adaptive Histogram Equalization (CLAHE).
- Runs EasyOCR across enhanced and original frames, applying deduplication and regex sanitization to filter out video artifacts.
- Loads `Qwen/Qwen2-VL-2B-Instruct` in fp16 to generate frame-level visual descriptions.
- Loads `Qwen/Qwen2.5-1.5B-Instruct` to consolidate raw extraction artifacts into schema-compliant JSON objects.
- Performs ground-truth verification against local context files when available.

---

## Step 3: Semantic Chunking & FAISS Vector Indexing

- Constructs text representations tagged with source identity (transcript, recipe_info, visual_frame).
- Encodes chunks into 384-dimensional dense vectors using `sentence-transformers/all-MiniLM-L6-v2`.
- Normalizes embeddings via $L_2$ norm and builds an inner-product FAISS index (`IndexFlatIP`).
- Persists index files into `FAISS_Index/video_rag.index` and metadata mapping into `FAISS_Index/chunks_metadata.json`.

---

## Step 4: Lexical Keyword Indexing & Search (BM25)

- Concatenates video titles, ingredients, cooking steps, audio transcripts, and OCR/visual captions into document strings.
- Tokenizes and cleans document corpora, removing punctuation and non-alphanumeric noise.
- Constructs an in-memory BM25Okapi index to support term-matching keyword queries.

---

## Step 5: Knowledge Graph Construction & Visualization

- Maps video metadata into a directed NetworkX graph (`DiGraph`).
- Normalizes entity nodes across five functional classes:
  - Dish
  - Cuisine
  - Ingredient
  - Step
  - Utensil/Object
- Establishes directional semantic relationships between entities.
- Serializes the graph structure into `Knowledge_Graph/video_rag_kg.graphml`.
- Renders an auto-scaled layout plot with node color coding and edge labels into `Knowledge_Graph/knowledge_graph.png`.

---

# Configuration & Setup

## Environment Variables

Set the API keys in your environment or Kaggle Secrets:

```bash
export SARVAM_API_KEY="your_sarvam_api_key"
export HF_TOKEN="your_huggingface_token"
```

If `SARVAM_API_KEY` is not present in the environment or secrets table, the script will prompt for input via `getpass`.

---

# Usage Example

## Running the Full Pipeline

Execute the pipeline sequentially within a Python environment or Jupyter notebook context:

```python
# 1. Run Pipeline Processing (Step 1 & Step 2)
# Generates keyframes, audio transcripts, YOLO labels, VLM captions, and structured JSON.

# 2. Build Dense Index (Step 3)
# Encodes chunks and generates FAISS vector storage.

# 3. Build Lexical Index & Run Test Query (Step 4)

from step4_bm25 import search_lexical_bm25

results = search_lexical_bm25("mustard oil fish curry", top_k=3)

for r in results:
    print(f"Score: {r['bm25_score']:.4f} | Dish: {r['dish']} | File: {r['file']}")

# 4. Generate Knowledge Graph (Step 5)
# Outputs GraphML file and visual plot in /Knowledge_Graph/
```

---
# Schema & Output Specifications

## Metadata JSON Schema Output (`Metadata/<video_id>_metadata.json`)

```json
{
  "video_info": {
    "video_id": "string",
    "video_name": "string",
    "title": "string",
    "category": "Cooking",
    "language": "bn",
    "duration": 0.0,
    "fps": 0.0,
    "width": 0,
    "height": 0,
    "total_frames": 0,
    "file_size": "string",
    "video_path": "string"
  },
  "recipe_information": {
    "dish_type": "string",
    "ingredients": [
      "string"
    ],
    "estimated_steps": [
      "string"
    ],
    "tips": [
      "string"
    ],
    "cuisine": "string",
    "tags": [
      "string"
    ]
  },
  "audio_information": {
    "transcript_bn": "string",
    "transcript_en": "string",
    "timestamps": [
      {
        "start": 0.0,
        "end": 0.0,
        "text": "string"
      }
    ]
  },
  "shot_information": [
    {
      "shot_id": "string",
      "start_time": 0.0,
      "end_time": 0.0,
      "duration": 0.0,
      "keyframe_path": "string"
    }
  ],
  "frame_information": [
    {
      "frame_id": "string",
      "shot_id": "string",
      "timestamp": 0.0,
      "frame_path": "string",
      "ocr_text": "string"
    }
  ],
  "object_detection": [
    {
      "frame_id": "string",
      "shot_id": "string",
      "detected_objects": [
        {
          "class_name": "string",
          "confidence": 0.0,
          "bbox": [
            0.0,
            0.0,
            0.0,
            0.0
          ]
        }
      ]
    }
  ],
  "visual_descriptions": [
    {
      "frame_id": "string",
      "shot_id": "string",
      "description": "string",
      "ocr_text": "string"
    }
  ]
}
```