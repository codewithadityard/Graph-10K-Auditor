import os
import instructor
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

ollama_base = OpenAI(
    base_url="http://localhost:11434/v1", 
    api_key="ollama" 
    )


ollama_client = instructor.from_openai(
    ollama_base, 
    mode=instructor.Mode.JSON
    )



gemini_base = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

gemini_client = instructor.from_openai(
    gemini_base,
    mode=instructor.Mode.TOOLS
)