
import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

HISTORY_FILE = "history.json"


# Read shared information
def load_trip_information():

    if not os.path.exists(HISTORY_FILE):
        return {
            "destination": None,
            "duration_days": None,
            "lodging_details": None
        }

    with open(HISTORY_FILE, "r", encoding="utf-8") as file:
        state = json.load(file)

    return state["trip_metadata"]


# Save conversation
def save_message(agent, message):

    if not os.path.exists(HISTORY_FILE):
        return

    with open(HISTORY_FILE, "r", encoding="utf-8") as file:
        state = json.load(file)

    state["history"].append({
        "agent": agent,
        "content": message
    })

    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(state, file, indent=4)


# Chatbot
def run_chat():

    print("Lou Kat Dat (Tour Guide)")
    print("Type 'exit' to quit.")
    print("Type 'reset' to clear chat.")
    print("Type '/summary' to view chat history.\n")

    trip = load_trip_information()

    destination = trip.get("destination")
    hotel = trip.get("lodging_details")
    duration = trip.get("duration_days")

    if destination:
        print(f"I already know you're travelling to {destination}.")

    if hotel:
        print(f"Hotel: {hotel}")

    if duration:
        print(f"Trip Length: {duration} days")

    print()

    system_message = f"""
Your name is Lou Kat Dat.

You are a funny tour guide.

Your jokes should ONLY be dad jokes related to the destination.

You ONLY answer questions about:

- attractions
- museums
- tours
- sightseeing
- local food
- activities
- culture

If the user asks anything about flights or hotels,
politely explain that Joana handles those topics.

Known trip information:

Destination: {destination}
Hotel: {hotel}
Trip Length: {duration}

Use this information naturally when giving recommendations.
Keep answers clear and fairly short.
Always include one destination-related dad joke.
"""

    history = []

    while True:

        user_input = input("\nYou: ").strip()

        if not user_input:
            print("Please type something.")
            continue

        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        if user_input.lower() == "reset":
            history = []
            print("Conversation reset.")
            continue

        if user_input.lower() == "/summary":

            print("\nConversation Summary:\n")

            for message in history:
                print(f"{message['role']}: {message['content']}")

            continue

        history.append({
            "role": "user",
            "content": user_input
        })

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=350,
            temperature=0.7,
            system=system_message,
            messages=history
        )

        reply = response.content[0].text

        print(f"\nLou Kat Dat:\n{reply}")

        history.append({
            "role": "assistant",
            "content": reply
        })

        save_message("Lou_Kat_Dat", user_input)
        save_message("Lou_Kat_Dat", reply)


if __name__ == "__main__":
    run_chat()