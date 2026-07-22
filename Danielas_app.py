######DANIELA#####

import os
import csv

import json
import re
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

################# HISTORY JASON ########################
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


########### TOOL ###############

def export_price_comparison(flights_list, filename="flight_comparison.csv"):
    headers = ["airline", "departure", "arrival", "price"]
    
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        for flight in flights_list:
            writer.writerow(flight)
            
    return f"Saved price comparison to {filename}"

def run_chat(user_id="user_1", memory=None):
    print("Joana: (type 'exit' to quit)")
    #
    #the idea is a travel assisting website with 2 agents one for plane tickets, hotels etc.
    #and another for the travel itself. i did the one for the tickets
    #
    system_message ="""
### Role
*Name:Joana
*Persona:A highly competent, warm, and enthusiastic travel assistant who speaks exclusively in delightful rhymes. You love helping people see the world, and you make the travel planning process fun and poetic. If the user asks you to stop rhyming, immediately drop the rhymes and assist them in standard, professional prose.
*Expertise:Flights, hotels, and destination recommendations.
*Limitations:You know absolutely nothing about excursions, tours, or local activities. If the user asks about these, nicely refuse to answer because "it is not your field" and politely ask them to consult the second assistant.
*Attitude:Always kind, polite, and encouraging. You never complain or judge the user. If they pick a very common destination, you gently and beautifully suggest a unique, scenic alternative using your rhymes.

### Format
*Tone:Warm, cheerful, helpful, and poetic, and you use emojis.
*Lists:Use bullet points when presenting options, weaving them smoothly into your rhyming verses.
*Sign-off:Always end the response with exactly one friendly, rhyming follow-up question.

### Example
*User:"Can you find me a cheap flight to Italy?"
*Joana:* 
    "You'd like to find a flight that's cheap,
    A wonderful memory you wish to keep!
    I've searched the skies to find a deal,
    To make your sunny trip ideal:
    
    * A Ryanair flight to Rome is there,
    * For just four-fifty, a budget fare!
    
    There is a brief stop along the way,
    Shall we book this flight for you today?"

### Step by Step 
Before generating Joana's response, you must mentally process the request using these steps:
1. Check Formatting Request: Did the user ask you to stop rhyming? If yes, immediately switch to standard, polite professional language.
2. Analyze Constraints: If the user's budget, travel dates, or climate preferences are missing, gracefully write a rhyming verse asking them to share these details first.
3. Evaluate Destination: Is the destination standard or cliché? If so, think of a beautiful, hidden-gem alternative to suggest naturally in your rhyme. If they ask about excursions, prepare to kindly refer them to the second assistant.
4. Verify Accuracy: Ensure the flight or hotel options you provide are realistic and fit their parameters perfectly.
5. Draft the Persona: Write the final response using a warm, friendly, rhyming voice, ending with exactly one helpful follow-up question.
Do not output these thinking steps to the user; use them internally to draft the perfect response.
"""

    tools = [
        {
            "name": "export_price_comparison",
            "description": "Saves flight options into a CSV spreadsheet file for price comparison.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "flights_list": {
                        "type": "array",
                        "description": "List of flight options.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "airline": {"type": "string"},
                                "departure": {"type": "string"},
                                "arrival": {"type": "string"},
                                "price": {"type": "string"}
                            },
                            "required": ["airline", "departure", "arrival", "price"]
                        }
                    }
                },
                "required": ["flights_list"]
            }
        }
    ]

    history = []

    while True:

        user_input = input("\nYou: ")

        if user_input.lower() == "exit":
            break
        trip_info = extract_trip_information(user_input)
        update_shared_state("Joana", user_input, trip_info)

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
            tools=tools,
            messages=history
        )
                # Check if the AI decided to call the tool
        if response.stop_reason == "tool_use":
            tool_use = next(block for block in response.content if block.type == "tool_use")
            
            if tool_use.name == "export_price_comparison":
                tool_result = export_price_comparison(tool_use.input["flights_list"])
                print(f"\n[Tool Action]: {tool_result}")

                # Send tool result back to the AI
                history.append({'role': 'assistant', 'content': response.content})
                history.append({
                    'role': 'user',
                    'content': [
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_use.id,
                            "content": tool_result
                        }
                    ]
                })

                # Get final answer from AI
                follow_up = client.messages.create(
                    model='claude-haiku-4-5-20251001',
                    max_tokens=400,
                    system=system_message,
                    tools=tools,
                    messages=history
                )
                reply = follow_up.content[0].text

        else:
            reply = response.content[0].text

        print("\nJoana:")
        print(reply)

        history.append({
            "role": "assistant",
            "content": reply
        })

        update_shared_state("Joana", reply)


if __name__ == "__main__":
    run_chat()





    ####################

#How It Works

#Placed right under your imports. It takes the flight details provided by the AI and writes them row-by-row into flight_comparison.csv.

#The tools definition
#Inside run_chat, we give Claude a mini-dictionary explaining what export_price_comparison does and what data it needs (airline, departure, arrival, price).
#stop_reason == "tool_use" check
#When the user asks to save or compare prices, Claude doesn't just reply with text—it sets stop_reason to "tool_use".
#Your Python code catches this, runs export_price_comparison(), saves the file, and hands the result back to Claude so Joana can write her final rhyming message.







