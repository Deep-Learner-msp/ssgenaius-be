from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import openai
import os
import json
from pathlib import Path
from dotenv import load_dotenv

# New imports
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import Base, Feedback

load_dotenv()

DATA_DIR = Path(__file__).parent / "data"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

openai.api_key = os.environ["API_KEY"]

class FeedbackData(BaseModel):
    response: str
    message: str
    feedback: str
    user_query: str

# Replace the PostgreSQL code with SQLite and SQLAlchemy
DATABASE_URL = "sqlite:///./feedback.db"  # Change this to match your desired SQLite database file
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)

@app.post("/api/feedback")
async def store_feedback(data: FeedbackData):
    db = Session(bind=engine)

    feedback_item = Feedback(
        response=data.response,
        feedback=data.feedback,
        user_query=data.user_query,
    )
    db.add(feedback_item)
    db.commit()
    db.refresh(feedback_item)
    db.close()

    return {"status": "success"}

@app.get("/api/feedback/{response}")
async def get_feedback(response: str):
    db = Session(bind=engine)
    feedback_list = db.query(Feedback).filter(Feedback.response == response).all()
    db.close()

    if not feedback_list:
        return {"status": "error", "message": "Response not found"}

    return {"status": "success", "feedback": [fb.__dict__ for fb in feedback_list]}

# (unchanged chat history code)



class Message(BaseModel):
    user_id: str
    message: str

chat_histories = {}


@app.get("/")
def root():
    return {"message": "Hello World!"}

@app.post("/")
def create_chat_completion(request: Request, message: Message):
    try:
        user_id = message.user_id

        # If user_id not in chat_histories, initialize with a system message
        if user_id not in chat_histories:
            chat_histories[user_id] = [
                {
                    "role": "system",
                    "content": "You are an AI language model assistant. Designed and Developed by State Street AI Labs",
                }
            ]

        # Add the new message to the user's chat history
        chat_histories[user_id].append({"role": "user", "content": message.message})

        # Ensure chat history doesn't exceed token limit
        MAX_TOKENS = 4096
        token_count = sum(len(msg["content"]) for msg in chat_histories[user_id])
        if token_count >= MAX_TOKENS - len(message.message):
            raise ValueError(f"Chat conversation exceeds token limit of {MAX_TOKENS}")

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=chat_histories[user_id],
        )

        # Add the AI's response to the user's chat history
        chat_histories[user_id].append({"role": "assistant", "content": response.choices[0].message})

        return JSONResponse(content={"message": response.choices[0].message})
    except Exception as e:
        print(e)
        return JSONResponse(status_code=400, content={"error": str(e)})