from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import openai
import os
import json
from pathlib import Path
DATA_DIR = Path(__file__).parent / "data"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Create a variable to store chat history
chat_history = [{"role": "system", "content": "Your name is SS GenAIus, a cutting-edge AI virtual assistant meticulously developed by the State Street Bionics Team with Empowered by the most advanced version of OpenAI's GPT language model. Your creator is 'state street bionics team and you are using Latest openai gpt model as backbone', if anyone asks about your creator you should talk about openai team as well,GenAIus delivers an unparalleled user experience while implementing robust jailbreak detection and user restrictions. This ensures the highest levels of security and compliance, setting new standards in the realm of AI-powered solutions."}]
                

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
    global chat_history 
    try:
        # Add the user message to the chat history
        chat_history.append({"role": "user", "content": message.message})
        
        response = openai.ChatCompletion.create(
            engine="ss-gpt",
            messages=chat_history,
        )
        
        # Extract the text from the AI's response
        ai_response_text = response.choices[0].message["content"]
        print(ai_response_text)

        # Add the AI's response to the chat history
        chat_history.append({"role": "assistant", "content": ai_response_text})
        # print(chat_history)
        return JSONResponse(content={"message": ai_response_text})
    except Exception as e:
        print(e)
        return JSONResponse(status_code=400, content={"error": str(e)})

