# Chatbot
This is a RAG pipeline built on llama-index framework and uses OpenAI API for generating responses to user queries.
The chatbot offers career counseliing, including document indexing and chat history management.

## Installation
1. Clone the repository
```bash
git clone https://github.com/suryanshgupta9933/chatbot.git

cd chatbot
```
2. Install the dependencies
```bash
pip install -r requirements.txt
```
3. Change the .env file for updating the upload directory path
```bash
UPLOAD_FOLDER = 'path_to_your_upload_directory'
```
4. Run the application from the root directory

## Endpoints
1. Uploading the pdf file to the server `src/API/upload.py`
```bash
python -m src.API.upload
```
- `/upload` - Upload the pdf in the upload directory(temporary storage)

2. Chat with the model `src/API/chat.py`
```bash
python -m src.API.chat
```
- Index Documents 
    - URL: `/index-documents`
    - Method: POST
    - Headers: 
        - Content-Type: multipart/form-data
    - Request Body:
        - file: pdf file
    - Response: 
    ```
    {
        "message": "Documents indexed successfully",
        "filename": "<filename>"
    }
    ```

- Chat with the model
    - URL: `/chat`
    - Method: POST
    - Headers: 
        - Content-Type: application/json
    - Request Body:
    ```
    {
        "message": "<user_query>"
    }
    ```
    - Response:
    ```
    {
        "response": "<response>"
    }
    ```

- Return Chat History
    - URL: `/get-chat-history`
    - Method: GET
    - Response:
    ```
    {
        "chat_history": [
            {
                "role": "<role>",
                "content": "<content>",
                "additional_kwargs": "<additional_kwargs>"
            }
        ]
    }
    ```

- Update Chat History
    - URL: `/set-chat-history`
    - Method: POST
    - Headers: 
        - Content-Type: application/json
    - Request Body:
    ```
    [
        {
            "role": "<role>",
            "content": "<content>",
            "additional_kwargs": "<additional_kwargs>"
        }
    ]
    ```
    - Response:
    ```
    {
        "message": "Chat history updated successfully"
    }
    ```

- Reset Chat History
    - URL: `/reset-chat-history`
    - Method: POST
    - Response:
    ```
    {
        "message": "Chat history reset successfully"
    }
    ```

## Prompt
The system message is stored in the `src/rag/prompt.py` file. The prompt can be updated as per the requirement.

> **_NOTE:_** There is a field `role` in the chat history for `MessageRole.USER` which is used to pass the user details to the chatbot.