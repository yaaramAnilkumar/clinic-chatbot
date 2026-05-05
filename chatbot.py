import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def get_response(conversation_history, system_prompt):
    """Send conversation to Claude and get a response"""
    
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=500,
        system=system_prompt,
        messages=conversation_history
    )
    
    return response.content[0].text