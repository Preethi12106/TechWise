from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent import run_agent
from database import create_table


app = FastAPI(title="TechWise API")

create_table()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def home():
    return {"message": "TechWise API is running"}


@app.post("/chat")
def chat(request: ChatRequest):
    response = run_agent(request.message)

    return {
        "response": response
    }