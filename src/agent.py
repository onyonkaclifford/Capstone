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

#correct
# import os
# import chromadb

# from langchain_community.document_loaders import PyPDFLoader
# # from langchain.embeddings.openai import OpenAIEmbeddings
# # from langchain_community.embeddings import OpenAIEmbeddings
# # from langchain.vectorstores import Chroma
# from langchain_community.vectorstores import Chroma
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.schema import Document
# from langchain_core.messages import AIMessage, HumanMessage
# from langchain_openai import ChatOpenAI

# from langchain_openai import OpenAIEmbeddings

# from langchain.agents import AgentExecutor
# from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
# from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


# class Agent:
#     def __init__(self, model, temperature, max_tokens, verbose, pdf_directory="docs/"):
#         self._chat_history = []

#         # Initialize ChromaDB
#         self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
#         self.collection = self.chroma_client.get_or_create_collection(name="pdf_docs")

#         # Load PDFs into vector database
#         self.pdf_directory = pdf_directory
#         self.embedding_model = OpenAIEmbeddings()
#         self._load_pdfs_into_db()

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
#                     "agent_scratchpad": lambda x: format_to_openai_tool_messages(
#                         x["intermediate_steps"]
#                     ),
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
#         return ChatPromptTemplate.from_messages(
#             [
#                 ("system", "You are a PR2 robot controlling assistant that get users instructions on what to do with the robot and take their instructions. also you can answer them accordingly based on what is in the documents."),
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

#     def _load_pdfs_into_db(self):
#         """Loads and embeds PDFs into ChromaDB"""
#         all_documents = []
#         for pdf_file in os.listdir(self.pdf_directory):
#             if pdf_file.endswith(".pdf"):
#                 loader = PyPDFLoader(os.path.join(self.pdf_directory, pdf_file))
#                 pages = loader.load()

#                 # Split text into smaller chunks for better search results
#                 text_splitter = RecursiveCharacterTextSplitter(
#                     chunk_size=500, chunk_overlap=50)
#                 chunks = text_splitter.split_documents(pages)

#                 for chunk in chunks:
#                     all_documents.append(
#                         {"text": chunk.page_content, "metadata": {"source": pdf_file}})

#         # Store in ChromaDB
#         for doc in all_documents:
#             self.collection.add(
#                 documents=[doc["text"]],
#                 metadatas=[doc["metadata"]],
#                 ids=[str(hash(doc["text"]))]
#             )
#         print(" PDFs have been embedded and stored in ChromaDB!")

#     def _retrieve_relevant_docs(self, query, top_k=3):
#         """Fetches the most relevant document chunks for the query"""
#         search_results = self.collection.query(query_texts=[query], n_results=top_k)

#         results = search_results["documents"][0]
#         return results if results else ["No relevant document found."]

#     def handle_message(self, message_text, base64_images, base64_images_mimes):
#         """Handles incoming messages, retrieves documents, and generates responses."""
#         image_url = (
#             None
#             if len(base64_images) == 0
#             else f"data:{base64_images_mimes[0]};base64,{base64_images[0]}"
#         )

#         # Retrieve relevant documents before generating a response
#         docs = self._retrieve_relevant_docs(message_text)
#         context = "\n".join(docs)

#         # Inject retrieved context into query
#         full_input = f"Context:\n{context}\n\nUser Query: {message_text}"

#         result = (
#             self._agent_executor_without_image.invoke(
#                 {"input": full_input, "chat_history": self._chat_history}
#             )
#             if image_url is None
#             else self._agent_executor_with_image.invoke(
#                 {
#                     "input": full_input,
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

# agent.py

# agent.py

import os
import chromadb
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.agents import AgentExecutor, Tool
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Import the simulated tools
from simulated_tools import move_robot_simulated, spawn_objects_simulated, pick_and_place_simulated

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

        # Define the tools
        self.tools = [
            Tool(
                name="move_robot",
                func=move_robot_simulated,
                description="Move the robot to a new position. Parameters: {'position': [x, y, z]}"
            ),
            Tool(
                name="spawn_objects",
                func=spawn_objects_simulated,
                description="Spawn an object with a given name, color, and position. Parameters: {'name': str, 'color': str, 'position': [x, y, z]}"
            ),
            Tool(
                name="pick_and_place",
                func=pick_and_place_simulated,
                description="Pick up an object and place it at a new position. Parameters: {'name': str, 'position': [x, y, z]}"
            )
        ]

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
            tools=self.tools,
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
            tools=self.tools,
            verbose=verbose,
        )

    @staticmethod
    def _get_prompt_template(with_image=True):
        return ChatPromptTemplate.from_messages(
            [
                ("system", "You are a PR2 robot controlling assistant that gets user instructions on what to do with the robot and takes their instructions. "
                "You can also answer questions based on the documents. You have access to tools for moving the robot, spawning objects, and picking/placing objects."
                " Use these tools when appropriate."),
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
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=500, chunk_overlap=50)
                chunks = text_splitter.split_documents(pages)

                for chunk in chunks:
                    all_documents.append(
                        {"text": chunk.page_content, "metadata": {"source": pdf_file}})

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
# import chromadb
# from langchain_community.document_loaders import PyPDFLoader
# from langchain_community.vectorstores import Chroma
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.schema import Document
# from langchain_core.messages import AIMessage, HumanMessage
# from langchain_openai import ChatOpenAI, OpenAIEmbeddings
# from langchain.agents import AgentExecutor, Tool
# from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
# from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# # Import the simulated tools
# from simulated_tools import move_robot_simulated, spawn_objects_simulated, pick_and_place_simulated

# class Agent:
#     def __init__(self, model, temperature, max_tokens, verbose, pdf_directory="docs/"):
#         self._chat_history = []

#         # Initialize ChromaDB
#         self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
#         self.collection = self.chroma_client.get_or_create_collection(name="pdf_docs")

#         # Clear the collection to avoid duplicate entries
#         try:
#             # Use a valid filter condition to delete all documents
#             self.collection.delete(where={"id": {"$ne": ""}})
#         except Exception as e:
#             print(f"Error clearing ChromaDB collection: {e}")

#         # Load PDFs into vector database
#         self.pdf_directory = pdf_directory
#         self.embedding_model = OpenAIEmbeddings()
#         self._load_pdfs_into_db()

#         # Define the tools
#         self.tools = [
#             Tool(
#                 name="move_robot",
#                 func=move_robot_simulated,
#                 description="Move the robot to a new position. Parameters: {'position': [x, y, z]}"
#             ),
#             Tool(
#                 name="spawn_objects",
#                 func=spawn_objects_simulated,
#                 description="Spawn an object with a given name, color, and position. Parameters: {'name': str, 'color': str, 'position': [x, y, z]}"
#             ),
#             Tool(
#                 name="pick_and_place",
#                 func=pick_and_place_simulated,
#                 description="Pick up an object and place it at a new position. Parameters: {'name': str, 'position': [x, y, z]}"
#             )
#         ]

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
#                 | ChatOpenAI(model=model, temperature=temperature, max_tokens=max_tokens)
#                 | OpenAIToolsAgentOutputParser()
#             ),
#             tools=self.tools,
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
#                 | ChatOpenAI(model=model, temperature=temperature, max_tokens=max_tokens)
#                 | OpenAIToolsAgentOutputParser()
#             ),
#             tools=self.tools,
#             verbose=verbose,
#         )

#     @staticmethod
#     def _get_prompt_template(with_image=True):
#         return ChatPromptTemplate.from_messages(
#             [
#                 ("system", "You are a PR2 robot controlling assistant that gets user instructions on what to do with the robot and takes their instructions. You can also answer questions based on the documents. You have access to tools for moving the robot, spawning objects, and picking/placing objects. Use these tools when appropriate."),
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

#     def _load_pdfs_into_db(self):
#         """Loads and embeds PDFs into ChromaDB"""
#         all_documents = []
#         for pdf_file in os.listdir(self.pdf_directory):
#             if pdf_file.endswith(".pdf"):
#                 loader = PyPDFLoader(os.path.join(self.pdf_directory, pdf_file))
#                 pages = loader.load()

#                 # Split text into smaller chunks for better search results
#                 text_splitter = RecursiveCharacterTextSplitter(
#                     chunk_size=500, chunk_overlap=50)
#                 chunks = text_splitter.split_documents(pages)

#                 for chunk in chunks:
#                     all_documents.append(
#                         {"text": chunk.page_content, "metadata": {"source": pdf_file}})

#         # Store in ChromaDB
#         for doc in all_documents:
#             # Check if the document already exists in the collection
#             existing_docs = self.collection.get(
#                 where={"metadata.source": doc["metadata"]["source"]}
#             )
#             if not existing_docs["documents"]:  # Only add if it doesn't exist
#                 self.collection.add(
#                     documents=[doc["text"]],
#                     metadatas=[doc["metadata"]],
#                     ids=[str(hash(doc["text"]))]
#                 )
#         print("PDFs have been embedded and stored in ChromaDB!")

#     def _retrieve_relevant_docs(self, query, top_k=3):
#         """Fetches the most relevant document chunks for the query"""
#         search_results = self.collection.query(query_texts=[query], n_results=top_k)

#         results = search_results["documents"][0]
#         return results if results else ["No relevant document found."]

#     def handle_message(self, message_text, base64_images, base64_images_mimes):
#         """Handles incoming messages, retrieves documents, and generates responses."""
#         image_url = (
#             None
#             if len(base64_images) == 0
#             else f"data:{base64_images_mimes[0]};base64,{base64_images[0]}"
#         )

#         # Retrieve relevant documents before generating a response
#         docs = self._retrieve_relevant_docs(message_text)
#         context = "\n".join(docs)

#         # Inject retrieved context into query
#         full_input = f"Context:\n{context}\n\nUser Query: {message_text}"

#         result = (
#             self._agent_executor_without_image.invoke(
#                 {"input": full_input, "chat_history": self._chat_history}
#             )
#             if image_url is None
#             else self._agent_executor_with_image.invoke(
#                 {
#                     "input": full_input,
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