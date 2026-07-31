# Multimodal Video Retrieval-Augmented Generation (Video-RAG)

## Overview

This repository contains the implementation of a **Multimodal Video Retrieval-Augmented Generation (Video-RAG)** system. The project extracts rich multimodal metadata from videos and enables semantic search and question answering using both textual and visual information.

---

# Layer 1 – Metadata Generation Pipeline

Layer 1 is responsible for transforming raw videos into structured metadata that can later be indexed and retrieved by the RAG pipeline.

## Workflow

```
Input Video
      │
      ▼
Scene Detection
      │
      ▼
Key Frame Extraction
      │
      ├──────────────► OCR
      │
      ├──────────────► Object Detection (YOLOv8)
      │
      ├──────────────► Audio Extraction
      │                     │
      │                     ▼
      │               Speech-to-Text (Whisper)
      │
      └──────────────► Gemini Vision Analysis
                           │
                           ▼
                Structured JSON Metadata
```

## Technologies Used

* Python
* OpenCV
* PySceneDetect
* Faster-Whisper
* YOLOv8
* EasyOCR
* Deeptranslate
* Google Gemini API
* FFmpeg
* MediaInfo

## Metadata Generated

Each video is processed to generate:

* Video information
* Scene timestamps
* Keyframes
* Object detection results
* OCR text
* Audio transcription
* Visual scene descriptions
* Temporal metadata
* Final structured JSON

The generated JSON serves as the knowledge base for the Text-RAG and Graph-RAG retrieval pipelines.

---

# Dataset

>The below drive link contains all the videos with the code and JSON files of the videos

```
https://drive.google.com/drive/folders/1yQ4O2axm-QOxsG5lasseEsFhOoFdtTZn?usp=sharing
```

---



# UI Structure

```
Home
│
├── Upload Video
│
├── Metadata Generation
│      ├── Scene Detection
│      ├── OCR Results
│      ├── Object Detection
│      ├── Audio Transcript
│      └── Generated JSON
│
├── Video Search
│      ├── Text Query
│      ├── Similar Videos
│      └── Retrieved Segments
│
├── Chat with Videos
│      ├── Ask Questions
│      ├── Retrieved Context
│      └── Gemini Response
│
└── Analytics
       ├── Processing Time
       ├── Metadata Statistics
       └── Retrieval Performance
```

---

# Installation

```bash
git clone <repository-url>
cd Video-RAG

pip install -r requirements.txt
```



