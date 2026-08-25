# Zoro

Zoro is a local-first personal desktop assistant for macOS. It can respond with voice, accept voice input, use a local LLM, remember user-approved information locally, understand visible screen text using OCR, open websites, perform simple web searches, and show transparent activity logs.

## Features

- Start, wake, and stop assistant states
- Animated floating assistant bubble
- Expand/collapse dashboard
- Wake-style visual modes
- Voice wake-word command handling
- Mac voice output using the local `say` command
- Browser voice input
- Local LLM answers with Ollama
- Memory-aware responses
- Natural casual response style
- Local private memory
- Memory dashboard
- Delete individual memories or all memories
- Local activity log
- Local screen capture
- Local OCR with Tesseract
- LLM-based screen summaries
- Open common websites
- Start web searches

## Project Structure

```text
zoro
├── .gitignore
├── README.md
├── requirements.txt
├── backend
│   ├── main.py
│   └── memories.json
├── desktop
│   └── index.html
├── docs
│   ├── PROJECT_SUMMARY.md
│   └── RUNNING.md
└── screenshots
    └── screen-...png