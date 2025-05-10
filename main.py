from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import uvicorn
import asyncio

from fastapi.middleware.cors import CORSMiddleware

from google import genai
from google.genai import types
import time

from PROMPTS import system_prompts

from dotenv import load_dotenv
import os

load_dotenv()
gemini_key = os.getenv("GEMINI_API_KEY")

# Gemeni Cliet
client = genai.Client(api_key=gemini_key)

# Create chat
chat = client.chats.create(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction=system_prompts,
            temperature=0.3
        ),
)


from pydantic import BaseModel

# Define a request schema
class ChatRequest(BaseModel):
    query: str

# FASTAPI
app = FastAPI(title= "VEDA-PUTRA spiritual AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://127.0.0.1:5500"] if serving from local server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/', methods=['GET', 'HEAD', 'POST'])
def read_root():
    return {"msg": "Welcome to Veda-putra"}

@app.post('/chat')
async def chat_with_ai(request: ChatRequest):
    user_prompt = request.query
    # user_prompt = body.get("query", "")
    
    if not user_prompt:
        return {"error": "Query cannot be empty"}
    
    async def stream_response():
        response = chat.send_message_stream(user_prompt)
        yield "🟢 Assistant: "
        for chunk in response:
            try:
                if chunk.text:
                    yield chunk.text
                    await asyncio.sleep(0.1)
            except Exception as e:
                yield f"\nError : {e}\n"
        
    return StreamingResponse(stream_response(), media_type="text/plain")

                    
if __name__ == '__main__':
    uvicorn.run(app)