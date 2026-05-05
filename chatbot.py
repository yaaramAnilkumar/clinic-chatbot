import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def get_response(conversation_history, system_prompt):
    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=500,
            system=system_prompt,
            messages=conversation_history
        )
        if response.content and len(response.content) > 0:
            return response.content[0].text
        return "Sorry, I couldn't process that. Please try again!"

    except Exception as e:
        print(f"❌ Claude API error: {e}")
        return f"Sorry, I'm having difficulties. Please call 080-12345678."