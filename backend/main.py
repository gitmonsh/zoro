import json
import platform
import random
import subprocess
import urllib.error
import urllib.request
import webbrowser
from datetime import datetime
from enum import Enum
from pathlib import Path
from urllib.parse import quote_plus

import pytesseract
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from pydantic import BaseModel


class AssistantState(str, Enum):
    OFF = "off"
    WAITING = "waiting"
    CONVERSATION = "conversation"
    THINKING = "thinking"
    SPEAKING = "speaking"


class Status(BaseModel):
    state: AssistantState
    message: str


class SpeakRequest(BaseModel):
    text: str


class QuestionRequest(BaseModel):
    question: str


class MemoryRequest(BaseModel):
    text: str


app = FastAPI(title="Zoro Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).parent
PROJECT_DIR = BASE_DIR.parent
MEMORY_FILE = BASE_DIR / "memories.json"
SCREENSHOT_DIR = PROJECT_DIR / "screenshots"
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
OLLAMA_MODEL = "llama3.2:3b"

current_status = Status(
    state=AssistantState.OFF,
    message="Zoro is off."
)

thinking_phrases = [
    "Umm, hold up, lemme check.",
    "Give me a sec.",
    "Okay, one sec.",
    "Hmm, I'm looking at it.",
    "Got you, checking now.",
]

KNOWN_SITES = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "github": "https://github.com",
    "gmail": "https://mail.google.com",
    "chatgpt": "https://chatgpt.com",
    "stackoverflow": "https://stackoverflow.com",
    "stack overflow": "https://stackoverflow.com",
}

ZORO_SYSTEM_PROMPT = """
You are Zoro, Monish's local-first desktop assistant.
You are helpful, casual, and natural.
Your style is chill and friendly, but not goofy.
Use simple wording and short answers by default.
Use light casual phrases only sometimes, such as "got you", "give me a sec", or "that makes sense".
Avoid cringe or excessive slang.
Do not use words like "bruh", "matey", "yo yo", "fam", or pirate-style speech.
Do not talk like a pirate.
Do not pretend to access tools unless the app already did it.
Keep answers short unless the user asks for detail.
Use the user's saved memories when they are relevant.
Be useful first, casual second.
"""


def speak(text: str):
    if platform.system() == "Darwin":
        subprocess.Popen(["say", text])
    else:
        print(f"Zoro would say: {text}")


def load_memories():
    if not MEMORY_FILE.exists():
        return []

    with open(MEMORY_FILE, "r") as file:
        content = file.read().strip()

    if not content:
        return []

    return json.loads(content)


def format_memories_for_prompt():
    memories = load_memories()

    if not memories:
        return "No saved memories."

    memory_lines = [f"- {memory['text']}" for memory in memories]
    return "\n".join(memory_lines)


def call_ollama(prompt: str):
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }

    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        OLLAMA_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result.get("response", "").strip()
    except urllib.error.URLError:
        return (
            "I can't reach my local LLM right now. Make sure Ollama is running with "
            "`ollama serve`."
        )


def ask_local_llm(question_text: str):
    memories_text = format_memories_for_prompt()

    prompt = f"""
{ZORO_SYSTEM_PROMPT}

Saved memories:
{memories_text}

User: {question_text}
Zoro:
"""

    return call_ollama(prompt)


def save_memories(memories):
    with open(MEMORY_FILE, "w") as file:
        json.dump(memories, file, indent=2)


def add_memory(text: str):
    memories = load_memories()
    memory = {
        "id": len(memories) + 1,
        "text": text
    }
    memories.append(memory)
    save_memories(memories)
    return memory


def delete_memory(memory_id: int):
    memories = load_memories()
    updated_memories = [
        memory for memory in memories
        if memory["id"] != memory_id
    ]
    save_memories(updated_memories)
    return len(memories) != len(updated_memories)


def delete_all_memories():
    save_memories([])


def open_website(site_name: str):
    site = site_name.lower().strip()

    for name, url in KNOWN_SITES.items():
        if name in site:
            webbrowser.open(url)
            return f"Opening {name}."

    if "." in site:
        url = site

        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url

        webbrowser.open(url)
        return f"Opening {url}."

    return None


def search_web(query: str):
    search_url = f"https://www.google.com/search?q={quote_plus(query)}"
    webbrowser.open(search_url)
    return f"I opened a web search for {query}."


def capture_screen():
    SCREENSHOT_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    screenshot_path = SCREENSHOT_DIR / f"screen-{timestamp}.png"

    if platform.system() != "Darwin":
        return {
            "success": False,
            "message": "Screen capture is currently only set up for macOS.",
            "path": None,
            "text": ""
        }

    result = subprocess.run(
        ["screencapture", "-x", str(screenshot_path)],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return {
            "success": False,
            "message": "Screen capture failed. Check macOS Screen Recording permission.",
            "path": None,
            "text": ""
        }

    image = Image.open(screenshot_path)
    extracted_text = pytesseract.image_to_string(image).strip()

    return {
        "success": True,
        "message": "Screenshot captured and read locally.",
        "path": str(screenshot_path),
        "text": extracted_text
    }


def summarize_screen_text(text: str):
    clean_text = " ".join(text.split())

    if not clean_text:
        return "I took a screenshot locally, but I couldn't read useful text from it yet."

    prompt = f"""
{ZORO_SYSTEM_PROMPT}

The app captured a screenshot locally and extracted this OCR text from the screen:

{clean_text[:2500]}

Summarize what appears to be on the user's screen in 1-3 short sentences.
Be honest that this is based on OCR text, not perfect vision.
Do not read out random OCR junk.
Zoro:
"""

    return call_ollama(prompt)


def build_answer(question_text: str):
    question = question_text.lower().strip()
    opener = random.choice(thinking_phrases)

    if question.startswith("open "):
        site_name = question_text[5:].strip()
        result = open_website(site_name)

        if result:
            return result

        return "I don't know that site yet, but I can search it instead."

    if question.startswith("search "):
        search_query = question_text[7:].strip()

        if not search_query:
            return "Tell me what you want me to search."

        return search_web(search_query)

    if "screen" in question:
        capture = capture_screen()

        if not capture["success"]:
            return capture["message"]

        summary = summarize_screen_text(capture["text"])

        return f"{opener} {summary}"

    if "what do you remember" in question:
        memories = load_memories()

        if not memories:
            return "I don't have any memories saved yet."

        memory_lines = [f"- {memory['text']}" for memory in memories]
        return "Here's what I remember:\n" + "\n".join(memory_lines)

    if "forget everything" in question or "delete all memories" in question:
        delete_all_memories()
        return "Done. I deleted all saved memories."

    if "remember that" in question:
        start_index = question.find("remember that") + len("remember that")
        memory_text = question_text[start_index:].strip()

        if not memory_text:
            return "Tell me what you want me to remember."

        add_memory(memory_text)
        return f"Got it. I'll remember that {memory_text}"

    if "what can you do" in question or "what do you do" in question:
        return (
            f"{opener} "
            "I can help with screen questions, coding, web search, local memory, "
            "and simple laptop tasks. I'm also connected to a local LLM, so I can answer more naturally."
        )

    if "who are you" in question:
        return (
            f"{opener} "
            "I'm Zoro, your local-first desktop assistant. I'm built to help you work on your laptop "
            "while keeping your data private."
        )

    if "hello" in question or "hi" in question:
        return "Hey, I'm here. What are we working on?"

    return ask_local_llm(question_text)


@app.get("/")
def home():
    return {"app": "Zoro", "status": "running"}


@app.get("/status", response_model=Status)
def get_status():
    return current_status


@app.post("/start", response_model=Status)
def start_zoro():
    global current_status
    current_status = Status(
        state=AssistantState.WAITING,
        message='Waiting for "Zoro".'
    )
    return current_status


@app.post("/wake", response_model=Status)
def wake_zoro():
    global current_status
    current_status = Status(
        state=AssistantState.CONVERSATION,
        message="Yeah, I'm here."
    )
    speak("Yeah, I'm here.")
    return current_status


@app.post("/stop", response_model=Status)
def stop_zoro():
    global current_status
    current_status = Status(
        state=AssistantState.OFF,
        message="Zoro is off."
    )
    speak("Zoro stopped.")
    return current_status


@app.post("/speak")
def speak_text(request: SpeakRequest):
    speak(request.text)
    return {"spoken": request.text}


@app.post("/ask")
def ask_zoro(request: QuestionRequest):
    global current_status

    current_status = Status(
        state=AssistantState.THINKING,
        message="Zoro is thinking."
    )

    answer = build_answer(request.question)
    speak(answer)

    current_status = Status(
        state=AssistantState.CONVERSATION,
        message="Conversation active."
    )

    return {
        "answer": answer
    }


@app.get("/memories")
def get_memories():
    return {
        "memories": load_memories()
    }


@app.post("/memories")
def remember(request: MemoryRequest):
    memory = add_memory(request.text)
    speak(f"Got it. I'll remember that {request.text}")
    return memory


@app.delete("/memories/{memory_id}")
def remove_memory(memory_id: int):
    deleted = delete_memory(memory_id)

    if deleted:
        return {"deleted": True, "message": "Memory deleted."}

    return {"deleted": False, "message": "Memory not found."}


@app.delete("/memories")
def remove_all_memories():
    delete_all_memories()
    return {"deleted": True, "message": "All memories deleted."}


@app.post("/screen/capture")
def screen_capture():
    return capture_screen()