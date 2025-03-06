# from langchain.agents import AgentExecutor
# from langchain.agents.format_scratchpad.openai_tools import (
#     format_to_openai_tool_messages,
# )
# from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
# from langchain_core.messages import AIMessage, HumanMessage
# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain_openai import ChatOpenAI


# class Agent:
#     def __init__(self, model, temperature, max_tokens, verbose):
#         self._chat_history = []
#         self._agent_executor_with_image = AgentExecutor(
#             agent=(
#                 {
#                     "input": lambda x: x["input"],
#                     "image_url": lambda x: x["image_url"],
#                     "agent_scratchpad": lambda x: format_to_openai_tool_messages(
#                         x["intermediate_steps"]
#                     ),
#                     "chat_history": lambda x: x["chat_history"],
#                 }
#                 | Agent._get_prompt_template(with_image=True)
#                 | ChatOpenAI(
#                     model=model, temperature=temperature, max_tokens=max_tokens
#                 )
#                 | OpenAIToolsAgentOutputParser()
#             ),
#             tools=[],
#             verbose=verbose,
#         )
#         self._agent_executor_without_image = AgentExecutor(
#             agent=(
#                 {
#                     "input": lambda x: x["input"],
#                     "agent_scratchpad": lambda x: format_to_openai_tool_messages(
#                         x["intermediate_steps"]
#                     ),
#                     "chat_history": lambda x: x["chat_history"],
#                 }
#                 | Agent._get_prompt_template(with_image=False)
#                 | ChatOpenAI(
#                     model=model, temperature=temperature, max_tokens=max_tokens
#                 )
#                 | OpenAIToolsAgentOutputParser()
#             ),
#             tools=[],
#             verbose=verbose,
#         )

#     @staticmethod
#     def _get_prompt_template(with_image=True):
#         return ChatPromptTemplate.from_messages(
#             [
#                 ("system", "You are a question answering system"),
#                 MessagesPlaceholder(variable_name="chat_history"),
#                 (
#                     "human",
#                     (
#                         [
#                             {"type": "text", "text": "{input}"},
#                             {"type": "image_url", "image_url": "{image_url}"},
#                         ]
#                         if with_image
#                         else [{"type": "text", "text": "{input}"}]
#                     ),
#                 ),
#                 MessagesPlaceholder(variable_name="agent_scratchpad"),
#             ]
#         )

#     def handle_message(self, message_text, base64_images, base64_images_mimes):
#         image_url = (
#             None
#             if len(base64_images) == 0
#             else f"data:{base64_images_mimes[0]};base64,{base64_images[0]}"
#         )
#         result = (
#             self._agent_executor_without_image.invoke(
#                 {"input": message_text, "chat_history": self._chat_history}
#             )
#             if image_url is None
#             else self._agent_executor_with_image.invoke(
#                 {
#                     "input": message_text,
#                     "image_url": image_url,
#                     "chat_history": self._chat_history,
#                 }
#             )
#         )
#         self._chat_history.extend(
#             [
#                 HumanMessage(content=message_text),
#                 AIMessage(content=result["output"]),
#             ]
#         )

#         return result["output"]




import os
import chromadb

from langchain_community.document_loaders import PyPDFLoader
#from langchain.embeddings.openai import OpenAIEmbeddings
#from langchain_community.embeddings import OpenAIEmbeddings
#from langchain.vectorstores import Chroma
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI

from langchain_openai import OpenAIEmbeddings

from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


class Agent:
    def __init__(self, model, temperature, max_tokens, verbose, pdf_directory="docs/"):
        self._chat_history = []
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.chroma_client.get_or_create_collection(name="pdf_docs")

        # Load PDFs into vector database
        self.pdf_directory = pdf_directory
        self.embedding_model = OpenAIEmbeddings()
        self._load_pdfs_into_db()

        self._agent_executor_with_image = AgentExecutor(
            agent=(
                {
                    "input": lambda x: x["input"],
                    "image_url": lambda x: x["image_url"],
                    "agent_scratchpad": lambda x: format_to_openai_tool_messages(
                        x["intermediate_steps"]
                    ),
                    "chat_history": lambda x: x["chat_history"],
                }
                | Agent._get_prompt_template(with_image=True)
                | ChatOpenAI(model=model, temperature=temperature, max_tokens=max_tokens)
                | OpenAIToolsAgentOutputParser()
            ),
            tools=[],
            verbose=verbose,
        )
        self._agent_executor_without_image = AgentExecutor(
            agent=(
                {
                    "input": lambda x: x["input"],
                    "agent_scratchpad": lambda x: format_to_openai_tool_messages(
                        x["intermediate_steps"]
                    ),
                    "chat_history": lambda x: x["chat_history"],
                }
                | Agent._get_prompt_template(with_image=False)
                | ChatOpenAI(model=model, temperature=temperature, max_tokens=max_tokens)
                | OpenAIToolsAgentOutputParser()
            ),
            tools=[],
            verbose=verbose,
        )

    @staticmethod
    def _get_prompt_template(with_image=True):
        return ChatPromptTemplate.from_messages(
            [
                ("system", "You are a PR2 robot controlling assistant that get users instructions on what to do with the robot and take their instructions. also you can answer them accordingly based on what is in the documents."),
                MessagesPlaceholder(variable_name="chat_history"),
                (
                    "human",
                    (
                        [
                            {"type": "text", "text": "{input}"},
                            {"type": "image_url", "image_url": "{image_url}"},
                        ]
                        if with_image
                        else [{"type": "text", "text": "{input}"}]
                    ),
                ),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

    def _load_pdfs_into_db(self):
        """Loads and embeds PDFs into ChromaDB"""
        all_documents = []
        for pdf_file in os.listdir(self.pdf_directory):
            if pdf_file.endswith(".pdf"):
                loader = PyPDFLoader(os.path.join(self.pdf_directory, pdf_file))
                pages = loader.load()

                # Split text into smaller chunks for better search results
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
                chunks = text_splitter.split_documents(pages)

                for chunk in chunks:
                    all_documents.append({"text": chunk.page_content, "metadata": {"source": pdf_file}})

        # Store in ChromaDB
        for doc in all_documents:
            self.collection.add(
                documents=[doc["text"]],
                metadatas=[doc["metadata"]],
                ids=[str(hash(doc["text"]))]
            )
        print(" PDFs have been embedded and stored in ChromaDB!")

    def _retrieve_relevant_docs(self, query, top_k=3):
        """Fetches the most relevant document chunks for the query"""
        search_results = self.collection.query(query_texts=[query], n_results=top_k)

        results = search_results["documents"][0]
        return results if results else ["No relevant document found."]

    def handle_message(self, message_text, base64_images, base64_images_mimes):
        """Handles incoming messages, retrieves documents, and generates responses."""
        image_url = (
            None
            if len(base64_images) == 0
            else f"data:{base64_images_mimes[0]};base64,{base64_images[0]}"
        )
        
        # Retrieve relevant documents before generating a response
        docs = self._retrieve_relevant_docs(message_text)
        context = "\n".join(docs)

        # Inject retrieved context into query
        full_input = f"Context:\n{context}\n\nUser Query: {message_text}"

        result = (
            self._agent_executor_without_image.invoke(
                {"input": full_input, "chat_history": self._chat_history}
            )
            if image_url is None
            else self._agent_executor_with_image.invoke(
                {
                    "input": full_input,
                    "image_url": image_url,
                    "chat_history": self._chat_history,
                }
            )
        )
        
        self._chat_history.extend(
            [
                HumanMessage(content=message_text),
                AIMessage(content=result["output"]),
            ]
        )

        return result["output"]





















# import os
# import faiss
# import torch
# import numpy as np
# from PIL import Image
# from sentence_transformers import SentenceTransformer
# from langchain.agents import AgentExecutor
# from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
# from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
# from langchain_core.messages import AIMessage, HumanMessage
# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain_openai import ChatOpenAI


# class Agent:
#     def __init__(self, model, temperature, max_tokens, verbose):
#         self._chat_history = []
#         self.clip_model = SentenceTransformer("clip-ViT-B-32")
#         self.image_folder = "scene_images"
#         self.index_path = "image_index.faiss"
#         self.image_paths = []
#         self._load_faiss_index()

#         # Define two agents (one for text-only, one for text+image)
#         self._agent_executor_with_image = AgentExecutor(
#             agent=( 
#                 {
#                     "input": lambda x: x["input"],
#                     "image_url": lambda x: x["image_url"],
#                     "agent_scratchpad": lambda x: format_to_openai_tool_messages(x["intermediate_steps"]),
#                     "chat_history": lambda x: x["chat_history"],
#                 }
#                 | Agent._get_prompt_template(with_image=True)
#                 | ChatOpenAI(model=model, temperature=temperature, max_tokens=max_tokens)
#                 | OpenAIToolsAgentOutputParser()
#             ),
#             tools=[],
#             verbose=verbose,
#         )

#         self._agent_executor_without_image = AgentExecutor(
#             agent=( 
#                 {
#                     "input": lambda x: x["input"],
#                     "agent_scratchpad": lambda x: format_to_openai_tool_messages(x["intermediate_steps"]),
#                     "chat_history": lambda x: x["chat_history"],
#                 }
#                 | Agent._get_prompt_template(with_image=False)
#                 | ChatOpenAI(model=model, temperature=temperature, max_tokens=max_tokens)
#                 | OpenAIToolsAgentOutputParser()
#             ),
#             tools=[],
#             verbose=verbose,
#         )

#     @staticmethod
#     def _get_prompt_template(with_image=True):
#         """Define the system prompt template."""
#         return ChatPromptTemplate.from_messages(
#             [
#                 ("system", 
#                  "You are a scene understanding assistant for PR2 robot"),
#                 MessagesPlaceholder(variable_name="chat_history"),
#                 (
#                     "human",
#                     [
#                         {"type": "text", "text": "{input}"},
#                         {"type": "image_url", "image_url": "{image_url}"},
#                     ] if with_image else [{"type": "text", "text": "{input}"}],
#                 ),
#                 MessagesPlaceholder(variable_name="agent_scratchpad"),
#             ]
#         )

#     def _load_faiss_index(self):
#         """Load FAISS index and image paths."""
#         if os.path.exists(self.index_path):
#             self.index = faiss.read_index(self.index_path)
#             with open("image_paths.txt", "r") as f:
#                 self.image_paths = f.read().splitlines()
#         else:
#             self.index = faiss.IndexFlatL2(512)  # FAISS L2 Index for embeddings

#     def _save_faiss_index(self):
#         """Save FAISS index and image paths."""
#         faiss.write_index(self.index, self.index_path)
#         with open("image_paths.txt", "w") as f:
#             f.write("\n".join(self.image_paths))

#     def add_image_to_index(self, image_path):
#         """Add a new scene image to the FAISS index."""
#         image = Image.open(image_path)
#         image_embedding = self.clip_model.encode(image).astype(np.float32)
#         self.index.add(np.array([image_embedding]))
#         self.image_paths.append(image_path)
#         self._save_faiss_index()

#     def retrieve_images(self, query, top_k=2):
#         """Retrieve the most relevant images based on text query and understand them."""
#         query_embedding = self.clip_model.encode([query]).astype(np.float32)
#         distances, indices = self.index.search(query_embedding, top_k)
#         retrieved_images = [self.image_paths[i] for i in indices[0] if i < len(self.image_paths)]

#         # Process retrieved images to understand their content
#         image_features = [self.get_image_features(image_path) for image_path in retrieved_images]
#         return retrieved_images, image_features

#     def get_image_features(self, image_path):
#         """Extract features from an image for understanding."""
#         image = Image.open(image_path)
#         image_embedding = self.clip_model.encode(image).astype(np.float32)
#         # Optionally, use other models or techniques to interpret the image
#         return image_embedding

#     def handle_message(self, message_text, base64_images, base64_images_mimes):
#         """Handle user messages and perform RAG-based image retrieval and understanding."""
#         image_url = (
#             None
#             if len(base64_images) == 0
#             else f"data:{base64_images_mimes[0]};base64,{base64_images[0]}"
#         )

#         # If images are included, index them
#         if len(base64_images) > 0:
#             for i, base64_img in enumerate(base64_images):
#                 image_path = f"{self.image_folder}/image_{len(self.image_paths) + i}.jpg"
#                 img = Image.open(image_path)
#                 img.save(image_path)
#                 self.add_image_to_index(image_path)

#         # Retrieve relevant images and understand their contents
#         retrieved_images, image_features = self.retrieve_images(message_text)

#         # Generate response based on the text query and the image features
#         result = (
#             self._agent_executor_without_image.invoke(
#                 {"input": message_text, "chat_history": self._chat_history}
#             )
#             if image_url is None
#             else self._agent_executor_with_image.invoke(
#                 {"input": message_text, "image_url": image_url, "chat_history": self._chat_history}
#             )
#         )

#         self._chat_history.extend(
#             [
#                 HumanMessage(content=message_text),
#                 AIMessage(content=result["output"]),
#             ]
#         )

#         return result["output"], retrieved_images
