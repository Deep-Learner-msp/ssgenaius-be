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

openai.api_key = os.environ["API_KEY"]  # Ensure you have the API key in your environment variables
# openai.api_key = ""


class FeedbackData(BaseModel):
    response: str
    message: str
    feedback: str
    user_query: str


@app.post("/api/feedback")
async def store_feedback(data: FeedbackData):
    response_file = DATA_DIR / f"{data.message}.json"
    print(f"response_file: {response_file}")

    if not os.path.exists(response_file):
        with open(response_file, "w") as f:
            f.write("[]")

    with open(response_file, "r") as f:
        feedback_list = json.load(f)

    feedback_list.append({
      "user_query": data.user_query,
      "feedback": data.feedback
    })

    with open(response_file, "w") as f:
        json.dump(feedback_list, f)

    return {"status": "success"}


    # PostgreSQL database storage (commented out for future use)
    """
    import psycopg2

    # Replace with your own PostgreSQL connection details
    connection = psycopg2.connect(
        dbname="your_db_name",
        user="your_user",
        password="your_password",
        host="your_host",
        port="your_port"
    )

    cursor = connection.cursor()

    # Creating the table if it doesn't exist
    cursor.execute("""
        # CREATE TABLE IF NOT EXISTS feedback (
        #     id SERIAL PRIMARY KEY,
        #     response TEXT NOT NULL,
        #     feedback VARCHAR(255) NOT NULL
        # )
    """)
    connection.commit()

    # Inserting the feedback data into the table
    cursor.execute(
        "INSERT INTO feedback (response, feedback) VALUES (%s, %s)",
        (data.response, data.feedback)
    )
    connection.commit()

    cursor.close()
    connection.close()
    """

@app.get("/api/feedback/{response}")
async def get_feedback(response: str):
    response_file = DATA_DIR / f"{response}.json"

    if not os.path.exists(response_file):
        return {"status": "error", "message": "Response not found"}

    with open(response_file, "r") as f:
        feedback_list = json.load(f)

    return {"status": "success", "feedback": feedback_list}


class Message(BaseModel):
    message: str

@app.get("/")
def root():
    return {"message": "Hello World!"}

@app.post("/")
def create_chat_completion(request: Request, message: Message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an AI language model assistant. Designed and Developed by State Street AI Labs"},
                {"role": "user", "content": message.message},
            ],
        )
        return JSONResponse(content={"message": response.choices[0].message})
    except Exception as e:
        print(e)
        return JSONResponse(status_code=400, content={"error": str(e)})
