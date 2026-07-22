'''''
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
    '''''
import os
import json
from datetime import datetime
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
HISTORY_FILE = "history.json"
CALENDAR_FILE = "calendar.json"

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
    state["history"].append({"agent": agent, "content": message})
    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(state, file, indent=4)

# Calendar Execution Tool
def add_to_calendar(day_number, activity, time=None):
    """Saves a scheduled activity to the trip calendar."""
    if not os.path.exists(CALENDAR_FILE):
        calendar = {}
    else:
        with open(CALENDAR_FILE, "r", encoding="utf-8") as file:
            calendar = json.load(file)
    
    day_key = f"Day {day_number}"
    if day_key not in calendar:
        calendar[day_key] = []
        
    entry = {"activity": activity, "time": time or "All day"}
    calendar[day_key].append(entry)
    
    with open(CALENDAR_FILE, "w", encoding="utf-8") as file:
        json.dump(calendar, file, indent=4)
        
    return f"Success! Added '{activity}' to your trip calendar for Day {day_number}."

# Define the tool schema for Claude
calendar_tool_definition = {
    "name": "add_to_calendar",
    "description": "Add a planned activity or attraction to the specific day of the trip calendar.",
    "input_schema": {
        "type": "object",
        "properties": {
            "day_number": {
                "type": "integer",
                "description": "The specific day of the trip (e.g., 1, 2, 3) to add the activity to."
            },
            "activity": {
                "type": "string",
                "description": "The name of the activity, tour, or attraction."
            },
            "time": {
                "type": "string",
                "description": "The time of the activity (e.g., '14:00' or 'Morning'). Optional."
            }
        },
        "required": ["day_number", "activity"]
    }
}

# Chatbot
def run_chat():
    print("Lou Kat Dat (Tour Guide)")
    print("Type exit to quit.")
    print("Type reset to clear chat.")
    print("Type /summary to view chat history.\n")

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

    system_message = f"""Your name is Lou Kat Dat. You are a funny tour guide. Your jokes should ONLY be dad jokes related to the destination. 
You ONLY answer questions about:
- attractions
- museums
- tours
- sightseeing
- local food
- activities
- culture

If the user asks anything about flights or hotels, politely explain that Joana handles those topics. 
Known trip information: 
Destination: {destination} 
Hotel: {hotel} 
Trip Length: {duration} 
Use this information naturally when giving recommendations. Keep answers clear and fairly short. Always include one destination-related dad joke."""

    history = []
    
    # Available tools list
    tools = [calendar_tool_definition]

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

        history.append({"role": "user", "content": user_input})

        # Send request with available tools
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022", # Sonnet is highly recommended for reliable tool use
            max_tokens=350,
            temperature=0.7,
            system=system_message,
            messages=history,
            tools=tools
        )

        reply_blocks = response.content

        # Extract textual response
        reply = next((block.text for block in reply_blocks if block.type == "text"), "")

        # Check if Claude called a tool
        tool_use_blocks = [block for block in reply_blocks if block.type == "tool_use"]
        
        if tool_use_blocks:
            history.append({"role": "assistant", "content": reply_blocks})
            
            for tool_use in tool_use_blocks:
                tool_name = tool_use.name
                tool_inputs = tool_use.input
                tool_id = tool_use.id

                if tool_name == "add_to_calendar":
                    # Execute our Python function
                    tool_output = add_to_calendar(
                        day_number=tool_inputs.get("day_number"),
                        activity=tool_inputs.get("activity"),
                        time=tool_inputs.get("time")
                    )

                    # Send the tool result back to Claude
                    history.append({
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": tool_id,
                                "content": tool_output
                            }
                        ]
                    })

            # Claude gets the tool result and generates a final response
            follow_up_response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=350,
                temperature=0.7,
                system=system_message,
                messages=history,
                tools=tools
            )
            reply = follow_up_response.content[0].text

        print(f"\nLou Kat Dat:\n{reply}")
        
        # Append to message history for continuous chat context
        history.append({"role": "assistant", "content": reply})
        save_message("Lou_Kat_Dat", user_input)
        save_message("Lou_Kat_Dat", reply)

if __name__ == "__main__":
    run_chat()
    