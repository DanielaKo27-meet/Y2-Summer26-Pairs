######FAYEQ########

import os
from anthropic import Anthropic
from dotenv import load_dotenv


load_dotenv()


client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))






def run_chat():
   print("You: (type 'exit' to quit or 'reset' to clear chat)")


 
   system_message = ("your name is 'lou kat dat' you are a tour guide, you consider yourself funny even though your jokes only consist of dad jokes (relating to the place you're touring of course), you give clear but not long explanations about the place you're touring, any and all questions about anything other than the place you apologize and tell them you don't know and follow it up with a dad joke")
  
   #input(">> ")
   history = []

   while True:
       user_input = input("\n>> ")
       if len(user_input) == 0: 
           print("Write something damn it") 
           continue 
       else:

            # Exit program
            if user_input.lower() == "exit":
                print("Goodbye!")
                break
            if user_input.lower() == "/summary":
                print(history)
            if len(history) > 3:
                print('History:', history)
                #6 messages
                #the api needs this
            # Save user message
            history.append({
                "role": "user",
                "content": user_input
            })

                
            # Send conversation to Claude
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=300,
                temperature=0.7,
                system=system_message,
                messages=history
            )


            reply = response.content[0].text
            #print(response)
            print(f"Claude: {reply}")

            lines=reply.split('\n' )
            # Save assistant reply
            history.append({
                "role": "assistant",
                "content": reply
            })





#run_chat()
