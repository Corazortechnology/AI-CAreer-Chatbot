# Importing Dependencies
import logging
import os
from typing import List

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from chatbot import Chatbot

app = FastAPI()
# Configure CORS
orig_origins = [
    "http://localhost:3000",  # React app's URL
    "http://localhost:8000",  # Your FastAPI server URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=orig_origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Chat Request Model
class ChatRequest(BaseModel):
    message: str


# Initialize Chatbot
chatbot = Chatbot()


@app.post("/index-documents")
async def index_documents():
    try:
        chatbot.load_and_index_documents()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Documents indexed successfully"},
        )
    except Exception as e:
        logger.error(f"Error indexing documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while indexing documents",
        )


@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        response = chatbot.chat(request.message)
        return JSONResponse(
            status_code=status.HTTP_200_OK, content={"response": response}
        )
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the chat request",
        )


@app.get("/get-chat-history")
async def get_chat_history():
    try:
        chat_history = chatbot.return_chat_history()
        return JSONResponse(
            status_code=status.HTTP_200_OK, content={"chat_history": chat_history}
        )
    except Exception as e:
        logger.error(f"Error retrieving chat history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the chat history",
        )


@app.post("/set-chat-history")
async def set_chat_history(chat_history: List[dict]):
    try:
        chatbot.set_chat_history(chat_history)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Chat history updated successfully"},
        )
    except Exception as e:
        logger.error(f"Error setting chat history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while setting the chat history",
        )


@app.post("/reset-chat-history")
async def reset_chat_history():
    try:
        chatbot.reset_chat_history()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Chat history reset successfully"},
        )
    except Exception as e:
        logger.error(f"Error resetting chat history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while resetting the chat history",
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
