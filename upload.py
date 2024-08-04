# Importing Dependencies
import os
import shutil
import logging
import secrets
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, HTTPException, File, status
from fastapi.responses import JSONResponse

app = FastAPI()

# Load environment variables
load_dotenv()
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)