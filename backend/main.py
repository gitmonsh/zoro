import json
import platform
import random
import subprocess
from datetime import datetime
from enum import Enum
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

current_status = Status(
    state=AssistantState.OFF,
    message="Zoro is off."
)

thinking_phrases = [
    "Umm, hold up, lemme check.",
    "Bet, give me a sec.",
    "Okay, one sec.",
    "Hmm, I'm looking at it.",
    "Got you, checking now.",
]


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


def capture_screen():
    SCREENSHOT_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    screenshot_path = SCREENSHOT_DIR / f"screen-{timestamp}.png"

    if platform.system() != "Darwin":
        return {
            "success": False,
            "message": "Screen capture is currently only set up for macOS.",
            "path": None
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
            "path": None
        }

    return {
        "success": True,
        "message": "Screenshot captured locally.",
        "path": str(screenshot_path)
    }


def build_answer(question_text: str):
    question = question_text.lower().strip()
    opener = random.choice(thinking_phrases)

    if "screen" in question:
        capture = capture_screen()

        if capture["success"]:
            return (
                f"{opener} "
                "I took a temporary screenshot locally. Next we'll add OCR so I can actually read and explain it."
            )

        return capture["message"]

    if "what do you remember" in question:
        memories = load_memories()

        if not memories:
            return "I don't have any memories saved yet."

        memory_lines = [f"- {memory['text']}" for memory in memories]
        return "Here's what I remember:\n" + "\n".join(memory_lines)

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
            "and simple laptop tasks. I'm still early right now, but that's the direction."
        )

    if "who are you" in question:
        return (
            f"{opener} "
            "I'm Zoro, your local-first desktop assistant. I'm built to help you work on your laptop "
            "while keeping your data private."
        )

    if "hello" in question or "hi" in question:
        return "Yo, I'm here. What are we working on?"

    return (
        f"{opener} "
        "I get what you're asking. I'm still in my early version, so I can't fully answer that yet, "
        "but soon I'll connect this to local AI, screen vision, memory, and web search."
    )


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


@app.post("/screen/capture")
def screen_capture():
    return capture_screen()