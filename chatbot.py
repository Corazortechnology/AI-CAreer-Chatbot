# Importing Dependencies
import os

from dotenv import load_dotenv
from llama_index.core import (
    Settings,
    SimpleDirectoryReader,
    VectorStoreIndex,
    get_response_synthesizer,
)
from llama_index.core.llms import ChatMessage, MessageRole

# from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.retrievers.bm25 import BM25Retriever
from src.prompt import get_chat_prompt

# Load environment variables
load_dotenv()
UPLOAD_DIRECTORY = os.getenv("UPLOAD_DIRECTORY")

# Setting the LLM model
Settings.llm = OpenAI(model="gpt-4o-mini")


# Defining the Chatbot class
class Chatbot:
    def __init__(
        self,
        input_dir=UPLOAD_DIRECTORY,
        required_exts=[".pdf"],
        buffer_size=1,
        breakpoint_percentile_threshold=95,
        similarity_top_k=2,
        similarity_cutoff=0.5,
        response_mode="tree_summarize",
    ):
        self.input_dir = input_dir
        self.required_exts = required_exts
        self.buffer_size = buffer_size
        self.breakpoint_percentile_threshold = breakpoint_percentile_threshold
        self.similarity_top_k = similarity_top_k
        self.similarity_cutoff = similarity_cutoff
        self.response_mode = response_mode
        self.files = []
        self.reader = None
        self.documents = []
        self.nodes = []
        self.embed_model = OpenAIEmbedding()
        # self.splitter = SemanticSplitterNodeParser(
        #     buffer_size=self.buffer_size,
        #     breakpoint_percentile_threshold=self.breakpoint_percentile_threshold,
        #     embed_model=self.embed_model)
        self.splitter = SentenceSplitter(chunk_size=512, chunk_overlap=100)
        self.postprocessor = SimilarityPostprocessor(
            similarity_cutoff=self.similarity_cutoff
        )
        self.response_synthesizer = get_response_synthesizer(
            response_mode=self.response_mode
        )
        self.bm25_retriever = None
        self.query_engine = None
        self.llm = OpenAI(model="gpt-4o-mini")
        self.chat_history = get_chat_prompt()

    def load_and_index_documents(self):
        current_files = set(os.listdir(self.input_dir))
        print(current_files)
        new_files = current_files - set(self.files)
        if new_files:
            self.reader = SimpleDirectoryReader(
                input_dir=self.input_dir, required_exts=self.required_exts
            )
            self.documents.extend(self.reader.load_data())
            self.nodes.extend(self.splitter.get_nodes_from_documents(self.documents))
            if len(self.nodes) < self.similarity_top_k:
                self.similarity_top_k = len(self.nodes)
            self.bm25_retriever = BM25Retriever.from_defaults(
                nodes=self.nodes, similarity_top_k=self.similarity_top_k
            )
            self.files = current_files

    def query(self, query_text):
        self.query_engine = RetrieverQueryEngine(
            retriever=self.bm25_retriever,
            response_synthesizer=self.response_synthesizer,
            node_postprocessors=[self.postprocessor],
        )
        response = self.query_engine.query(query_text)
        return response

    def chat(self, user_message):
        if os.path.exists(self.input_dir) and os.listdir(self.input_dir):
            bm25_nodes = self.bm25_retriever.retrieve(user_message)
            if len(self.postprocessor.postprocess_nodes(bm25_nodes)) > 0:
                response = self.query(user_message)
                assistant_message = response.response
                self.update_chat_history(user_message, assistant_message)
                return assistant_message
            else:
                self.update_chat_history(user_message)
                response = self.llm.chat(self.chat_history)
                assistant_message = response.message.content
                self.update_chat_history(assistant_message)
                return assistant_message
        else:
            self.update_chat_history(user_message)
            response = self.llm.chat(self.chat_history)
            assistant_message = response.message.content
            self.update_chat_history(assistant_message)
            return assistant_message

    def update_chat_history(self, user_message=None, assistant_message=None):
        if user_message:
            self.chat_history.extend(
                [ChatMessage(role=MessageRole.USER, content=user_message)]
            )
        if assistant_message:
            self.chat_history.extend(
                [ChatMessage(role=MessageRole.ASSISTANT, content=assistant_message)]
            )

    def return_chat_history(self):
        json_chat_history = []
        for chat in self.chat_history:
            json_chat_history.append(
                {
                    "role": chat.role.value,
                    "content": chat.content,
                    "additional_kwargs": chat.additional_kwargs,
                }
            )
        return json_chat_history

    def set_chat_history(self, json_chat_history):
        user_chat_history = []
        for chat in json_chat_history:
            user_chat_history.append(
                ChatMessage(
                    role=MessageRole(chat["role"]),
                    content=chat["content"],
                    additional_kwargs=chat["additional_kwargs"],
                )
            )
        self.chat_history = user_chat_history

    def reset_chat_history(self):
        self.chat_history = get_chat_prompt()
