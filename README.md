# Zoro

Zoro is a local-first personal desktop assistant for macOS. It can respond with voice, accept voice input, remember user-approved information locally, understand visible screen text using OCR, open websites, and perform simple web searches.

## Features

- Start, wake, and stop assistant states
- Mac voice output using the local `say` command
- Browser voice input
- Natural casual response style
- Floating-style assistant dashboard
- Local private memory
- Memory dashboard
- Delete individual memories or all memories
- Local screen capture
- Local OCR with Tesseract
- Screen text summary
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
│   └── PROJECT_SUMMARY.md
└── screenshots
    └── screen-...png