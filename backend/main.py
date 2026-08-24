import platform
import random
import subprocess
from enum import Enum

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


app = FastAPI(title="Zoro Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


def build_answer(question_text: str):
    question = question_text.lower().strip()
    opener = random.choice(thinking_phrases)

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
        return (
            "Yo, I'm here. What are we working on?"
        )

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