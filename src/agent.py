import json
import os
from typing import Any, Dict, List, Optional, Tuple

# Third-party imports
import numpy as np

# Standard library imports
import requests
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.tools import StructuredTool
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Local imports
from .robot_api import create_robot_api_tool, create_robot_commands_tool
from .robot_api.evaluation_tracker import set_user_input


class Agent:
    def __init__(
        self,
        model,
        temperature,
        max_tokens,
        pycram_api_host,
        system_message_text,
        requests_timeout,
        verbose=True,
        handle_parsing_errors=True,
        pdf_directory: str = "docs/",
        skip_execution: bool = False,
    ):
        self._chat_history = []
        self.pdf_directory = pdf_directory
        self.embedding_model = OpenAIEmbeddings()
        self.vector_store = self._initialize_vector_store(not skip_execution)

        tools = [
            Agent._get_hello_tool(),
            create_robot_api_tool(pycram_api_host, requests_timeout, skip_execution),
            create_robot_commands_tool(
                pycram_api_host, requests_timeout, skip_execution
            ),
            self._get_rag_tool(not skip_execution),
        ]
        llm = ChatOpenAI(model=model, temperature=temperature, max_tokens=max_tokens)

        self._agent_executor_with_image = AgentExecutor(
            agent=create_openai_tools_agent(
                llm,
                tools,
                Agent._get_prompt_template(system_message_text, with_image=True),
            ),
            tools=tools,
            verbose=verbose,
            handle_parsing_errors=handle_parsing_errors,
        )
        self._agent_executor_without_image = AgentExecutor(
            agent=create_openai_tools_agent(
                llm,
                tools,
                Agent._get_prompt_template(system_message_text, with_image=False),
            ),
            tools=tools,
            verbose=verbose,
            handle_parsing_errors=handle_parsing_errors,
        )

    def _initialize_vector_store(self, verbose) -> FAISS:
        """Initialize FAISS vector store with documents."""
        faiss_index_path = "faiss_index"

        # Check if we have documents to process
        docs = self._load_documents(verbose)

        if not docs:
            (
                print("No documents found to load into vector store.")
                if verbose
                else "No print"
            )
            # Initialize with a dummy document if no actual documents exist
            return FAISS.from_texts(
                ["No kitchen environment information available."], self.embedding_model
            )

        # Process documents and create vector store
        (
            print(f"Processing {len(docs)} documents for vector store...")
            if verbose
            else "No print"
        )
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = text_splitter.split_documents(docs)
        print(f"Created {len(chunks)} chunks from documents") if verbose else "No print"

        # Create and save vector store
        vector_store = FAISS.from_documents(chunks, self.embedding_model)
        vector_store.save_local(faiss_index_path)
        print(f"FAISS index saved to {faiss_index_path}") if verbose else "No print"

        return vector_store

    def _load_documents(self, verbose) -> List[Document]:
        """Load documents from PDF directory."""
        if not os.path.exists(self.pdf_directory):
            os.makedirs(self.pdf_directory)
            print(f"Created directory: {self.pdf_directory}") if verbose else "No print"
            return []

        all_docs = []
        pdf_files = [f for f in os.listdir(self.pdf_directory) if f.endswith(".pdf")]

        if not pdf_files:
            (
                print(f"No PDF files found in {self.pdf_directory}")
                if verbose
                else "No print"
            )
            return []

        print(f"Found {len(pdf_files)} PDF files to process") if verbose else "No print"

        for pdf_file in pdf_files:
            pdf_path = os.path.join(self.pdf_directory, pdf_file)
            try:
                print(f"Loading {pdf_file}...") if verbose else "No print"
                loader = PyPDFLoader(pdf_path)
                docs = loader.load()
                (
                    print(f"Loaded {len(docs)} pages from {pdf_file}")
                    if verbose
                    else "No print"
                )
                all_docs.extend(docs)
            except Exception as e:
                print(f"Error loading PDF {pdf_file}: {e}") if verbose else "No print"

        return all_docs

    def _get_rag_tool(self, verbose):
        """Create a tool for RAG search."""

        def rag_search(query: str) -> str:
            """Search for information in documents relevant to the query."""
            results = self._retrieve_relevant_docs(query, top_k=3, verbose=verbose)
            if results and results[0] != "No relevant document found.":
                joined_results = "\n\n".join(results)
                return f"Found relevant information in documents:\n\n{joined_results}"
            else:
                return "No relevant information found in documents about this topic."

        return StructuredTool.from_function(
            func=rag_search,
            name="RAGSearch",
            description="Use this tool to search for information about the kitchen environment, objects, or robot capabilities in the documentation. "
            "Use the parameter from the document to pass the robot functions.",
        )

    def _retrieve_relevant_docs(
        self, query: str, top_k: int = 3, verbose=True
    ) -> List[str]:
        """Retrieve relevant document chunks for a query."""
        try:
            docs_and_scores = self.vector_store.similarity_search_with_score(
                query, k=top_k
            )
            if docs_and_scores:
                # Debug print to verify retrieval
                (
                    print(
                        f"Retrieved {len(docs_and_scores)} documents for query: {query}"
                    )
                    if verbose
                    else "No print"
                )
                for i, (doc, score) in enumerate(docs_and_scores):
                    (
                        print(
                            f"Document {i + 1}, Score: {score:.4f}, Content preview: {doc.page_content[:100]}..."
                        )
                        if verbose
                        else "No print"
                    )

                return [
                    f"Document content: {doc.page_content}"
                    for doc, _ in docs_and_scores
                ]
            else:
                (
                    print("No relevant documents found for query:", query)
                    if verbose
                    else "No print"
                )
                return ["No relevant document found."]
        except Exception as e:
            print(f"Error retrieving documents: {e}") if verbose else "No print"
            return ["Error retrieving relevant documents."]

    @staticmethod
    def _get_prompt_template(system_message_text, with_image=False):
        return ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=system_message_text),
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

    @staticmethod
    def _get_hello_tool():
        """Returns a simple tool that greets the user."""
        return StructuredTool.from_function(
            func=lambda: "Hello I am RoboCRAM. How can I help?",
            name="Hello",
            description="Use this tool when asked who you are or about your identity",
        )

    def handle_message(
        self, message_text, base64_images, base64_images_mimes, print_markers=True
    ):
        """
        Process a user message and optional image input.

        Args:
            message_text: The text message from the user
            base64_images: List of base64 encoded images
            base64_images_mimes: List of mime types for the images

        Returns:
            The AI's response as a string
        """
        # Add a marker to show beginning of new output
        print("") if print_markers else "No print"
        print("=====================================") if print_markers else "No print"
        print("Processing new input message...") if print_markers else "No print"
        print(f"Received message: {message_text}") if print_markers else "No print"

        # Record the user input for evaluation
        set_user_input(message_text, verbose=print_markers)

        # Process image if available
        image_url = (
            None
            if len(base64_images) == 0
            else f"data:{base64_images_mimes[0]};base64,{base64_images[0]}"
        )

        # Invoke the appropriate agent based on whether an image was provided
        result = (
            self._agent_executor_without_image.invoke(
                {"input": message_text, "chat_history": self._chat_history}
            )
            if image_url is None
            else self._agent_executor_with_image.invoke(
                {
                    "input": message_text,
                    "image_url": image_url,
                    "chat_history": self._chat_history,
                }
            )
        )

        # Process the result
        if "output" in result:
            self._chat_history.extend(
                [
                    HumanMessage(content=message_text),
                    AIMessage(content=result["output"]),
                ]
            )
            return result["output"]
        else:
            return "An error occurred while processing your request."
