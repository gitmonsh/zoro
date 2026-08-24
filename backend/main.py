import platform
import random
import subprocess
from enum import Enum

from fastapi import FastAPI
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

    opener = random.choice(thinking_phrases)
    answer = (
        f"{opener} "
        f"You asked: {request.question}. "
        "Right now I'm still learning, but soon I'll connect this to screen vision, memory, and local AI."
    )

    speak(answer)

    current_status = Status(
        state=AssistantState.CONVERSATION,
        message="Conversation active."
    )

    return {
        "question": request.question,
        "answer": answer
    }