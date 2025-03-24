# #####################
# A fastapi REST Server to allow programmatic interactions with the agent
# The server supports response streaming to the client side
# To start the server run fastapi dev agent_api.py
# Navigate to /docs endpoint to see the API documentation
# ####################

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio
from support_agent import start_agent
import types
from pydantic import BaseModel
from shared_data import messages # For Agent's Message History

app = FastAPI()

# #####################
# Agent Endpoint
# ####################

#The request body
class RequestBody(BaseModel):
    user_prompt: str
    stream: bool = False

@app.post("/agent/chat")
async def chat(body: RequestBody):
    if body.stream == True:
        response = start_agent(body.user_prompt, body.stream)
        if isinstance(response, types.GeneratorType):
            async def stream():
                chunk_text = ""
                for chunk in response:
                    if "message" in chunk:
                        content = chunk["message"].get("content", "")
                        chunk_text += content
                        yield content
                        await asyncio.sleep(0.01)
                
                #Append to agent's message history
                messages.append({
                    "role": "assistant",
                    "content": chunk_text
                })
                
            return StreamingResponse(stream(), media_type="text/plain")
        else:
            return StreamingResponse(response["message"]["content"], media_type="text/plain")
    
    else:
        response = start_agent(body.user_prompt, body.stream)
        #Append to agent's message history
        messages.append({
            "role": "assistant",
            "content": response["message"]["content"] 
        })
        return response

