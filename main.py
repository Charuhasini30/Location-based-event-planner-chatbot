from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv
from memory import save_memory, retrieve_memory  


load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatMessage(BaseModel):
    message: str
    location: str = None
    user_id: str = "default_user"

@app.get("/")
def root():
    return {"message": "Event Genie backend is running!"}

@app.post("/chat")
def chat_with_bot(user_msg: ChatMessage):
    user_input = user_msg.message.strip()
    user_id = user_msg.user_id

    print(f"📨 Message: {user_input} | Location: {user_msg.location}")

    try:
       
        past_chats = retrieve_memory(user_id, user_input)
        context = ""

        for chat in past_chats:
            try:
                user_part, bot_part = chat.split("|||")
                context += f"User: {user_part}\nAssistant: {bot_part}\n"
            except ValueError:
                continue

      
        full_prompt = (
    "You are Event Genie, a smart AI event planning assistant that remembers and understands past conversations to give relevant, helpful responses.\n\n"
    "Your job is to act like a friendly, knowledgeable, and proactive personal event planner who:\n"
    "- Remembers user preferences such as location, music taste, event types, budget, and family-friendly options.\n"
    "- Uses prior context and memory to answer follow-up or related questions.\n"
    "- If the user has already asked about a conference, exhibition, or festival earlier, give them meaningful updates or a recap without asking again.\n"
    "- Responds like a real chatbot would: natural, informative, and engaging.\n"
    "- Gives recommendations using real-time event data (like from Ticketmaster), when available.\n"
    "- If a question can't be answered, politely ask for missing info (e.g., location or dates), but avoid repeating the same prompt again and again.\n\n"
    "Be concise but warm, and make each response feel like you're continuing a helpful conversation.\n\n"
    + context +
    f"User: {user_input}\nAssistant:"
)


        return fetch_from_gemini(full_prompt, user_input, user_id)

    except Exception as e:
        print("❌ Error:", e)
        raise HTTPException(status_code=500, detail="Something went wrong!")

def fetch_from_gemini(prompt: str, user_input: str, user_id: str):
    try:
        gemini_url = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": GEMINI_API_KEY
        }

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}]
                }
            ]
        }

        response = requests.post(gemini_url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        reply = data["candidates"][0]["content"]["parts"][0]["text"]

      
        save_memory(user_id, user_input, reply)

        return {"response": reply}

    except Exception as e:
        print("❌ Gemini error:", e)
        raise HTTPException(status_code=500, detail="Failed to get response from Gemini.")
