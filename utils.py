import os
import requests
from dotenv import load_dotenv
from google.generativeai import configure, GenerativeModel

load_dotenv()


configure(api_key=os.getenv("GEMINI_API_KEY"))
model = GenerativeModel("gemini-1.5-flash")

def generate_response(user_input, memory_data, event_data):
    context = ""
    if memory_data:
        for m in memory_data:
            if "|||" in m:
                user_msg, bot_msg = m.split("|||", 1)
                context += f"User said: {user_msg}\nBot replied: {bot_msg}\n"
            else:
                context += f"User previously said: {m}\n"

    events_context = "\n".join([
        f"- {e['name']} on {e['date']} at {e['venue']}" for e in event_data
    ]) or "No current events found."

    prompt = f"""
You are an intelligent, helpful event planning assistant chatbot.

The user asked: "{user_input}"

Past Memory:
{context if context else "No prior interactions."}

Real-Time Events in {event_data[0]['venue'] if event_data else 'the user location'}:
{events_context}

Respond by helping the user find suitable events or plan accordingly.
"""

    try:
        res = model.generate_content(prompt)
        return res.text
    except Exception as e:
        return f"Sorry, I encountered an error while generating a response: {e}"

def get_events(location):
    if not location.strip():
        return []
    api_key = os.getenv("TICKETMASTER_API_KEY")
    url = f"https://app.ticketmaster.com/discovery/v2/events.json?apikey={api_key}&city={location}&size=5"

    try:
        response = requests.get(url)
        data = response.json()
        events = []

        if "_embedded" in data:
            for e in data["_embedded"]["events"]:
                events.append({
                    "name": e["name"],
                    "date": e["dates"]["start"]["localDate"],
                    "venue": e["_embedded"]["venues"][0]["name"]
                })
        return events
    except Exception as e:
        print(f"Error fetching events: {e}")
        return []
