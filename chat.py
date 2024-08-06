# Importing Dependencies
import logging
import os
from typing import List
import shutil

from fastapi import FastAPI, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from chatbot import Chatbot

app = FastAPI()
# Configure CORS
orig_origins = [
    "http://localhost:3000",  # React app's URL
    "http://localhost:8000",  # Your FastAPI server URL
    "https://edlighten-ai.vercel.app",
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

UPLOAD_DIRECTORY = os.getenv("UPLOAD_DIRECTORY")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Directory to save uploaded files
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

# Limit file size
MAX_FILE_SIZE = 10 * 1024 * 1024 # 10 MB

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file type. Please upload a PDF.")

    if len(file.file.read()) > MAX_FILE_SIZE:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File size exceeds the limit.")

    file.file.seek(0)

    try:
        filename = file.filename
        file_location = os.path.join(UPLOAD_DIRECTORY, filename)
        
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"File {filename} uploaded successfully to {file_location}")
        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "File uploaded successfully", "filename": filename})
    except Exception as e:
        logger.error(f"Error occurred while uploading file {file.filename}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while uploading the file.")


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
