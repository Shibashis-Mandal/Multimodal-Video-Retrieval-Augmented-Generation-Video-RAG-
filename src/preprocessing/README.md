# Hybrid Text RAG for Bengali Cooking Videos

A multimodal Text Retrieval-Augmented Generation (Text RAG) pipeline for Bengali cooking videos. The project extracts information from video, audio, and text, converts it into structured knowledge, and builds a hybrid retrieval system using dense vector search and sparse keyword search.

## Features

- Video metadata extraction
- Shot detection using PySceneDetect
- Representative frame extraction
- OCR for on-screen text extraction
- Bengali to English text translation
- Audio extraction and speech transcription
- Audio-shot alignment
- Object detection using YOLO
- Visual description generation
- Recipe information extraction
- Searchable chunk generation
- Dense embedding generation using Sentence Transformers
- BM25 sparse indexing
- ChromaDB vector database
- Hybrid Dense + Sparse Retrieval

## Project Pipeline

```
Video
│
├── Video Loader
├── Shot Detector
├── Frame Extractor
├── OCR
├── Translator
├── Audio Extractor
├── Audio Transcriber
├── Audio Shot Alignment
├── Object Detector
├── Visual Description
├── Recipe Information
│
└── Master JSON
      │
      ▼
Chunk Generator
      │
      ├── Dense Embeddings
      ├── BM25 Index
      └── ChromaDB
              │
              ▼
      Hybrid Retriever
              │
              ▼
      Relevant Text Chunks
```

## Folder Structure

```
src/
│
├── preprocessing/
│   ├── 01_video_loader.py
│   ├── 02_shot_detector.py
│   ├── 03_frame_extractor.py
│   ├── 04_ocr.py
│   ├── 05_translator.py
│   ├── 06_audio_extractor.py
│   ├── 07_audio_transcriber.py
│   ├── 08_audio_shot_alignment.py
│   ├── 09_object_detector.py
│   ├── 10_visual_description.py
│   └── 11_recipe_information.py
│
├── indexing/
│   ├── 12_chunk_generator.py
│   ├── 13_dense_embedding.py
│   ├── 14_bm25_index.py
│   └── 15_chroma_db.py
│
└── retrieval/
    └── 16_hybrid_retriever.py
```

## Technologies Used

- Python
- OpenCV
- PySceneDetect
- EasyOCR
- Google Translator
- SarvamAI
- YOLO
- Sentence Transformers (all-MiniLM-L6-v2)
- ChromaDB
- BM25

## How to Run

Run the scripts in the following order:

```
01_video_loader.py
02_shot_detector.py
03_frame_extractor.py
04_ocr.py
05_translator.py
06_audio_extractor.py
07_audio_transcriber.py
08_audio_shot_alignment.py
09_object_detector.py
10_visual_description.py
11_recipe_information.py
12_chunk_generator.py
13_dense_embedding.py
14_bm25_index.py
15_chroma_db.py
16_hybrid_retriever.py
```

## Example Query

```
When is the milk added in caramel custard?
```

The system retrieves the most relevant recipe summary and frame-level chunks using a combination of semantic similarity (dense retrieval) and keyword matching (BM25).

## Future Work

- Knowledge Graph Construction
- Graph-based Retrieval
- Hybrid Graph RAG
- LLM-based Answer Generation
- Web Interface

## Author

**Debisha Paul**

B.Tech in Computer Science and Engineering (Data Science)

Indian Statistical Institute (ISI) Internship Project
