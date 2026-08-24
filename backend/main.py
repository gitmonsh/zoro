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


app = FastAPI(title="Zoro Backend")

current_status = Status(
    state=AssistantState.OFF,
    message="Zoro is off."
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
    return current_status


@app.post("/stop", response_model=Status)
def stop_zoro():
    global current_status
    current_status = Status(
        state=AssistantState.OFF,
        message="Zoro is off."
    )
    return current_status