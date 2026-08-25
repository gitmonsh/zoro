# Running Zoro

Zoro currently runs locally with a backend server, an Ollama local LLM server, and a browser-based dashboard.

## 1. Start Ollama

Open a terminal:

```bash
ollama serve
```

Leave this running.

## 2. Start Zoro Backend

Open a second terminal in the project folder:

```bash
uvicorn backend.main:app --reload
```

Leave this running.

## 3. Open Dashboard

Open this file in a browser:

```text
desktop/index.html
```

## Required Local Tools

- Python
- FastAPI
- Uvicorn
- Tesseract OCR
- Ollama
- `llama3.2:3b` model

## Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Install Tesseract

```bash
brew install tesseract
```

## Install Ollama Model

```bash
ollama pull llama3.2:3b
```

## Test Commands

```text
What can you do?
Explain FastAPI in simple words
Remember that I prefer chill explanations
What do you remember?
What is on my screen?
Open YouTube
Search Python FastAPI tutorial
Forget everything
```

## Voice Test

Click `Listen`, then say:

```text
Zoro what is on my screen
```

Zoro should wake, capture the screen locally, use OCR, summarize it with the local LLM, and answer out loud.