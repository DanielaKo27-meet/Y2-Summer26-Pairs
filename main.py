from logging import config

import Danielas_app as app1
import Fayeqs_app as app2

import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
client = Anthropic(api_key=api_key)

# 1. NEW: Enhanced tracking function that manages both text history AND explicit metadata transfers
def update_shared_state(agent_name, action_or_message, trip_info=None):
    history_file = "history.json"
    temp_file = "history.json.tmp"
    
    # Load or initialize the structured schema
    try:
        with open(history_file, "r", encoding="utf-8") as file:
            state = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        state = {
            "trip_metadata": {
                "destination": None,
                "duration_days": None,
                "lodging_details": None,
                "last_updated_by": None
            },
            "history": []
        }
    
    # Update the text logging array
    if action_or_message:
        state["history"].append({"agent": agent_name, "content": action_or_message})
    
    # Update the explicit variables passed from Daniela to Fayeq
    if trip_info:
        for key, value in trip_info.items():
            if key in state["trip_metadata"]:
                state["trip_metadata"][key] = value
        state["trip_metadata"]["last_updated_by"] = agent_name
    
    # Write atomically to prevent data loss
    try:
        with open(temp_file, "w", encoding="utf-8") as file:
            json.dump(state, file, indent=4, ensure_ascii=False)
        os.replace(temp_file, history_file)
    except Exception as e:
        if os.path.exists(temp_file):
            os.remove(temp_file)
        print(f"Error syncing data schema: {e}")

# System message stays the same as your setup...
system_message = "...(Your original Joana System Message)..."

def run_chat():
    print("You: (type exit to quit)")
    chat_history = []
    
    while True:
        user_input = input(">> ").strip()
        if not user_input or user_input.lower() == "exit":
            break
            
        chat_history.append({"role": "user", "content": user_input})
        
        # 2. EXAMPLE: Daniela tracks variables and explicitly sends them down the line
        # In production, you can parse this out of the input text or use a secondary function call.
        extracted_trip_data = {
            "destination": "Paris, France", 
            "duration_days": 5, 
            "lodging_details": "Le Meurice Hotel"
        }
        
        # Daniela saves the chat text AND explicitly updates the variables for Fayeq
        update_shared_state(
            agent_name="Daniela_Agent", 
            action_or_message=f"Processed user query: {user_input}",
            trip_info=extracted_trip_data
        )
        
        try:
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=400,
                system=system_message,
                messages=chat_history
            )
            reply = "".join([block.text for block in response.content if block.type == "text"])
            print(f"\nClaude: {reply}\n")
            
            chat_history.append({"role": "assistant", "content": reply})
            update_shared_state("Joana_Agent", reply)
            
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    run_chat()
