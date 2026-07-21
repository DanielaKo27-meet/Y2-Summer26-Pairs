
import os
import json
import re
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

HISTORY_FILE = "history.json"


# Create history file if needed
def initialize_history():

    if not os.path.exists(HISTORY_FILE):

        state = {
            "trip_metadata": {
                "destination": None,
                "duration_days": None,
                "lodging_details": None,
                "last_updated_by": None
            },
            "history": []
        }

        with open(HISTORY_FILE, "w", encoding="utf-8") as file:
            json.dump(state, file, indent=4)


# Save conversation + metadata
def update_shared_state(agent_name, message, trip_info=None):

    initialize_history()

    with open(HISTORY_FILE, "r", encoding="utf-8") as file:
        state = json.load(file)

    state["history"].append({
        "agent": agent_name,
        "content": message
    })

    if trip_info:

        for key, value in trip_info.items():

            if value:
                state["trip_metadata"][key] = value

        state["trip_metadata"]["last_updated_by"] = agent_name

    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(state, file, indent=4)


# Extract travel information
def extract_trip_information(text):

    trip = {}

    # Destination

    destination = re.search(r"(?:to|going to|traveling to|travelling to)\s+([A-Za-z ]+)", text, re.I)

    if destination:
        trip["destination"] = destination.group(1).strip()

    # Days

    days = re.search(r"(\d+)\s*days?", text, re.I)

    if days:
        trip["duration_days"] = int(days.group(1))

    # Hotel

    hotel = re.search(r"(?:hotel|staying at)\s+([A-Za-z0-9 ]+)", text, re.I)

    if hotel:
        trip["lodging_details"] = hotel.group(1).strip()

    return trip

# Check if user wants tours
def needs_second_agent(text):

    keywords = [
        "tour",
        "activity",
        "activities",
        "museum",
        "excursion",
        "things to do",
        "guide",
        "attraction",
        "attractions"
    ]

    text = text.lower()

    return any(word in text for word in keywords)


# Chatbot

def run_chat():

    print("Joana: (type 'exit' to quit)")

    system_message = """
### Role
Name: Joana

Persona:
You are a warm and enthusiastic travel assistant.

You always answer in rhyming verses.

If the user asks you to stop rhyming,
switch immediately to normal professional language.

You specialize ONLY in:

- Flights
- Hotels
- Destination recommendations

You DO NOT answer questions about:

- Tours
- Excursions
- Activities

If asked about these topics,
politely explain that another assistant handles them.

Always finish with exactly ONE follow-up question.
"""

    history = []

    while True:

        user_input = input("\nYou: ")

        if user_input.lower() == "exit":
            break

        trip_info = extract_trip_information(user_input)

        update_shared_state(
            "Joana",
            user_input,
            trip_info
        )

        if needs_second_agent(user_input):

            print("\nJoana:")
            print("That question belongs to our local tour guide.")
            print("Switching you to the second assistant...\n")

            return "handoff"

        history.append({
            "role": "user",
            "content": user_input
        })

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=350,
            temperature=0.8,
            system=system_message,
            messages=history
        )

        reply = response.content[0].text

        print("\nJoana:")
        print(reply)

        history.append({
            "role": "assistant",
            "content": reply
        })

        update_shared_state(
            "Joana",
            reply
        )


if __name__ == "__main__":
    run_chat()