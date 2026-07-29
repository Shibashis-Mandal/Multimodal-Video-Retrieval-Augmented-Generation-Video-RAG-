#  Multimodal Video Retrieval-Augmented Generation (Video RAG)

A **Multimodal Video Retrieval-Augmented Generation (Video RAG)** pipeline for Bengali recipe videos. This repository focuses on building a structured multimodal dataset and implementing a **Hybrid Text Retrieval-Augmented Generation (Text RAG)** system that enables efficient semantic and keyword-based retrieval of recipe information from cooking videos.

---

## Project Overview

The project converts raw cooking videos into structured multimodal data by extracting video metadata, recipe information, audio transcripts, shot information, frame information, object detections, and visual descriptions.

The extracted information is transformed into searchable text chunks, embedded into vector representations, indexed using BM25 and ChromaDB, and finally queried using a Hybrid Retrieval approach combining dense semantic search and sparse keyword search.

---

##  Features

- Video Metadata Extraction
- Shot Detection
- Frame Extraction
- OCR Extraction
- Bengali → English Translation
- Audio Extraction
- Audio Transcription
- Audio-Shot Alignment
- Object Detection (YOLO)
- Visual Description Generation
- Recipe Information Generation
- Chunk Generation
- Dense Embedding Generation
- BM25 Index Generation
- ChromaDB Vector Database Creation
- Hybrid Text Retrieval (Dense + Sparse)

---

#  Repository Structure

```text
Multimodal-Video-Retrieval-Augmented-Generation-Video-RAG-/
│
├── src/
│   │
│   ├── preprocessing/
│   │   ├── .gitkeep
│   │   ├── 01_video_loader.py
│   │   ├── 02_shot_detector.py
│   │   ├── 03_frame_extractor.py
│   │   ├── 04_ocr_extractor.py
│   │   ├── 05_translator.py
│   │   ├── 06_audio_extractor.py
│   │   ├── 07_audio_transcriber.py
│   │   ├── 08_audio_shot_aligner.py
│   │   ├── 09_object_detector.py
│   │   ├── 10_visual_description.py
│   │   ├── 11_recipe_information_generator.py
│   │   ├── 12_chunk_generator.py
│   │   ├── 13_dense_embedding.py
│   │   ├── 14_bm25_index.py
│   │   ├── 15_chroma_db.py
│   │   └── __init__.py
│   │
│   └── retrieval/
│       ├── 16_hybrid_retriever.py
│       └── __init__.py
│
├── Text_RAG_Recipe_Extraction_Pipeline.ipynb
├── requirement.txt
└── .gitignore
```

---

#  Pipeline Workflow

```
Video
   │
   ▼
Video Loader
   │
   ▼
Shot Detection
   │
   ▼
Frame Extraction
   │
   ▼
OCR Extraction
   │
   ▼
Translation
   │
   ▼
Audio Extraction
   │
   ▼
Audio Transcription
   │
   ▼
Audio-Shot Alignment
   │
   ▼
Object Detection
   │
   ▼
Visual Description Generation
   │
   ▼
Recipe Information Generation
   │
   ▼
Master JSON Creation
   │
   ▼
Chunk Generation
   │
   ▼
Dense Embeddings
   │
   ▼
BM25 Index
   │
   ▼
ChromaDB
   │
   ▼
Hybrid Text Retrieval
```

---

# 📝 Execution Order

Run the scripts sequentially.

| Step | Script | Purpose |
|------|---------|---------|
| 01 | `01_video_loader.py` | Extract video metadata |
| 02 | `02_shot_detector.py` | Detect shots in the video |
| 03 | `03_frame_extractor.py` | Extract representative frames |
| 04 | `04_ocr_extractor.py` | Extract on-screen text |
| 05 | `05_translator.py` | Translate OCR content |
| 06 | `06_audio_extractor.py` | Extract audio from video |
| 07 | `07_audio_transcriber.py` | Generate transcripts |
| 08 | `08_audio_shot_aligner.py` | Align transcripts with shots |
| 09 | `09_object_detector.py` | Detect objects using YOLO |
| 10 | `10_visual_description.py` | Generate frame descriptions |
| 11 | `11_recipe_information_generator.py` | Generate recipe metadata |
| 12 | `12_chunk_generator.py` | Generate retrieval chunks |
| 13 | `13_dense_embedding.py` | Create dense embeddings |
| 14 | `14_bm25_index.py` | Build BM25 index |
| 15 | `15_chroma_db.py` | Store embeddings in ChromaDB |
| 16 | `16_hybrid_retriever.py` | Perform Hybrid Text Retrieval |

---

#  Master JSON Structure

Each processed video generates a structured Master JSON containing:

- **video_info**
- **recipe_information**
- **audio_information**
- **shot_information**
- **frame_information**
- **object_detection**
- **visual_descriptions**

This JSON acts as the immutable source for all downstream retrieval tasks.

---

#  Chunk Types

The chunk generation module produces three different chunk categories:

### 1. Recipe Summary Chunk

Contains:

- Dish information
- Cuisine
- Ingredients
- Recipe steps

---

### 2. Shot Chunk

Contains:

- Shot ID
- Timestamp
- Audio transcript
- Bengali & English text

---

### 3. Frame Chunk

Contains:

- Frame ID
- Timestamp
- OCR text
- Detected objects
- Visual description

---

#  Hybrid Text Retrieval

The retrieval pipeline combines two complementary search methods:

### Dense Retrieval

- SentenceTransformers (`all-MiniLM-L6-v2`)
- Embedding Generation
- ChromaDB Vector Search
- Distance-based Semantic Retrieval

### Sparse Retrieval

- BM25 Keyword Matching
- Exact lexical search
- Ingredient and recipe term matching

### Hybrid Retrieval Logic

```
User Query
      │
      ▼
Generate Query Embedding
      │
      ├────────► ChromaDB (Dense Retrieval)
      │
      └────────► BM25 (Sparse Retrieval)
                    │
                    ▼
             Merge Results
                    │
           Remove Duplicates
                    │
             Rank Retrieved Chunks
                    │
                    ▼
             Final Hybrid Results
```

---

#  Technologies Used

| Category | Technology |
|----------|------------|
| Programming Language | Python |
| Computer Vision | OpenCV |
| Object Detection | YOLO |
| OCR | EasyOCR |
| Translation | Translator API |
| Audio Processing | FFmpeg |
| Speech Recognition | Sarvam AI |
| LLM | Ollama (Gemma 3) |
| Embeddings | SentenceTransformers |
| Dense Vector Store | ChromaDB |
| Sparse Retrieval | BM25 |
| Retrieval | Hybrid Dense + Sparse |

---

#  Output

The system generates:

- Master JSON files
- Recipe Summary Chunks
- Shot Chunks
- Frame Chunks
- Dense Embeddings
- BM25 Index
- ChromaDB Vector Database
- Hybrid Retrieval Results

---

#  Notebook

The repository also includes:

```
Text_RAG_Recipe_Extraction_Pipeline.ipynb
```

which demonstrates the complete Text RAG pipeline in a single notebook.

---

#  Contributor

**Debisha Paul**

**Module:** Layer 2 – Hybrid Text Retrieval-Augmented Generation (Text RAG)

**Internship Project:** Multimodal Video Retrieval-Augmented Generation (Video RAG)

---

