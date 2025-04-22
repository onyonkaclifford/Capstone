
import json
import os
from typing import List, Dict, Optional, Tuple, Any

import faiss
import numpy as np
import requests
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.tools import StructuredTool
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


class Agent:
    def __init__(
        self,
        model: str,
        temperature: float,
        max_tokens: int,
        pycram_api_host: str,
        system_message_text: str,
        requests_timeout: int,
        verbose: bool = True,
        handle_parsing_errors: bool = True,
        pdf_directory: str = "docs/",
    ):
        self._chat_history = []
        self.pdf_directory = pdf_directory
        self.embedding_model = OpenAIEmbeddings()
        
        # Log initial setup
        print(f"Initializing Agent with PDF directory: {pdf_directory}")
        
        # Create vector store and load documents
        self.vector_store = self._initialize_vector_store()
        
        tools = [
            Agent._get_hello_tool(),
            Agent._get_robot_tool(pycram_api_host, requests_timeout),
            Agent._get_robot_commands_tool(pycram_api_host, requests_timeout),
            self._get_rag_tool(),  # Add RAG as a tool
        ]
        
        llm = ChatOpenAI(model=model, temperature=temperature, max_tokens=max_tokens)

        # Create agent 
        system_message_with_rag = system_message_text + "\n\nWhen asked about the kitchen environment or objects, ALWAYS use the RAGSearch tool to gather information from documents before responding."
        
        self._agent_executor_with_image = AgentExecutor(
            agent=create_openai_tools_agent(
                llm,
                tools,
                Agent._get_prompt_template(system_message_with_rag, with_image=True),
            ),
            tools=tools,
            verbose=verbose,
            handle_parsing_errors=handle_parsing_errors,
            max_iterations=3,  # Allow multiple tool uses
        )
        
        self._agent_executor_without_image = AgentExecutor(
            agent=create_openai_tools_agent(
                llm,
                tools,
                Agent._get_prompt_template(system_message_with_rag, with_image=False),
            ),
            tools=tools,
            verbose=verbose,
            handle_parsing_errors=handle_parsing_errors,
            max_iterations=3,  # Allow multiple tool uses
        )

    def _initialize_vector_store(self) -> FAISS:
        """Initialize FAISS vector store with documents."""
        faiss_index_path = "faiss_index"
        
        # Check if we have documents to process
        docs = self._load_documents()
        
        if not docs:
            print("No documents found to load into vector store.")
            # Initialize with a dummy document if no actual documents exist
            return FAISS.from_texts(["No kitchen environment information available."], self.embedding_model)
        
        # Process documents and create vector store
        print(f"Processing {len(docs)} documents for vector store...")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = text_splitter.split_documents(docs)
        print(f"Created {len(chunks)} chunks from documents")
        
        # Create and save vector store
        vector_store = FAISS.from_documents(chunks, self.embedding_model)
        vector_store.save_local(faiss_index_path)
        print(f"FAISS index saved to {faiss_index_path}")
        
        return vector_store

    def _load_documents(self) -> List[Document]:
        """Load documents from PDF directory."""
        if not os.path.exists(self.pdf_directory):
            os.makedirs(self.pdf_directory)
            print(f"Created directory: {self.pdf_directory}")
            return []
        
        all_docs = []
        pdf_files = [f for f in os.listdir(self.pdf_directory) if f.endswith('.pdf')]
        
        if not pdf_files:
            print(f"No PDF files found in {self.pdf_directory}")
            return []
        
        print(f"Found {len(pdf_files)} PDF files to process")
        
        for pdf_file in pdf_files:
            pdf_path = os.path.join(self.pdf_directory, pdf_file)
            try:
                print(f"Loading {pdf_file}...")
                loader = PyPDFLoader(pdf_path)
                docs = loader.load()
                print(f"Loaded {len(docs)} pages from {pdf_file}")
                all_docs.extend(docs)
            except Exception as e:
                print(f"Error loading PDF {pdf_file}: {e}")
        
        return all_docs

    def _get_rag_tool(self):
        """Create a tool for RAG search."""
        def rag_search(query: str) -> str:
            """Search for information in documents relevant to the query."""
            results = self._retrieve_relevant_docs(query, top_k=3)
            if results and results[0] != "No relevant document found.":
                joined_results = "\n\n".join(results)
                return f"Found relevant information in documents:\n\n{joined_results}"
            else:
                return "No relevant information found in documents about this topic."
        
        return StructuredTool.from_function(
            func=rag_search,
            name="RAGSearch",
            description="Use this tool to search for information about the kitchen environment, objects, or robot capabilities in the documentation."
            "use the parameter from the document to pass the robot functions",
        )

    @staticmethod
    def _get_prompt_template(system_message_text, with_image=False):
        messages = [
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
        return ChatPromptTemplate.from_messages(messages)

    @staticmethod
    def _get_hello_tool():
        return StructuredTool.from_function(
            func=lambda: "Hello I am RoboCRAM. How can I help?",
            name="Hello",
            description="Use this tool when asked who you are or about your identity",
        )

    @staticmethod
    def _get_robot_tool(pycram_api_host, requests_timeout):
        def robot_api_tool(
            command: str = None,
            coordinates: list = None,
            object_name: str = None,
            target_location: list = None,
            arm: str = None,
            object_choice: str = None,
            color: str = None,
            perception_area: str = None,
            object_type: str = None,
            detection_area: str = None,
            **kwargs,
        ):
            # Check if command is provided
            if command is None:
                return "Please specify a robot command"

            # Collect all parameters into kwargs for easier handling
            all_params = {
                "coordinates": coordinates,
                "object_name": object_name,
                "target_location": target_location,
                "arm": arm,
                "object_choice": object_choice,
                "color": color,
                "perception_area": perception_area,
                "object_type": object_type,
                "detection_area": detection_area,
            }

            # Add any additional kwargs
            all_params.update(kwargs)

            # Remove None values
            all_params = {k: v for k, v in all_params.items() if v is not None}

            # Define required parameters for each command
            required_params = {
                "move_robot": ["coordinates"],
                "pickup_and_place": ["object_name", "target_location"],
                "transport_object": ["object_name", "target_location"],
                "spawn_objects": ["object_choice", "coordinates"],
                "look_for_object": ["object_name"],
                "detect_object": ["object_type"],
                "unpack_arms": [],  # No required params
            }

            # Check if command is valid
            if command not in required_params:
                return f"ERROR: Unknown command '{command}'"

            # Check for required parameters
            missing = [p for p in required_params[command] if p not in all_params]
            if missing:
                return (
                    f"ERROR: {command} command requires these missing parameters: {', '.join(missing)}. "
                    "Make sure to pass them explicitly by name."
                )

            # Validate parameter types and values
            if "coordinates" in all_params:
                if (
                    not isinstance(all_params["coordinates"], list)
                    or len(all_params["coordinates"]) != 3
                ):
                    return "ERROR: coordinates must be a list of exactly 3 values [x, y, z]"
                # Convert to float
                all_params["coordinates"] = [
                    float(c) for c in all_params["coordinates"]
                ]

            if "arm" in all_params and all_params["arm"] not in ["left", "right"]:
                return "ERROR: arm takes the values: 'left' or 'right']"

            # Prepare params for specific commands
            api_params = {}

            if command == "move_robot":
                api_params["coordinates"] = all_params["coordinates"]

            elif command == "pickup_and_place":
                api_params["object_name"] = all_params["object_name"]
                api_params["target_location"] = all_params["target_location"]
                if "arm" in all_params:
                    api_params["arm"] = all_params["arm"]

            elif command == "transport_object":
                api_params["object_name"] = all_params["object_name"]
                api_params["target_location"] = all_params["target_location"]
                if "arm" in all_params:
                    api_params["arm"] = all_params["arm"]

            elif command == "spawn_objects":
                api_params["object_choice"] = all_params["object_choice"]
                api_params["coordinates"] = all_params["coordinates"]
                if "color" in all_params:
                    api_params["color"] = all_params["color"]

            elif command == "look_for_object":
                api_params["object_name"] = all_params["object_name"]

            elif command == "detect_object":
                api_params["object_type"] = all_params["object_type"]
                if "detection_area" in all_params:
                    api_params["detection_area"] = all_params["detection_area"]

            elif command == "robot_perceive":
                if "perception_area" in all_params:
                    api_params["perception_area"] = all_params["perception_area"]

            # Make API call
            api_url = f"{pycram_api_host}/execute"
            response = requests.post(
                api_url,
                json={"command": command, "params": api_params},
                timeout=requests_timeout,
            )

            # Process response
            if response.status_code == 200:
                result = response.json()
                return json.dumps(result)
            else:
                return f"API error: {response.status_code} - {response.text}"

        return StructuredTool.from_function(
            func=robot_api_tool,
            name="RobotControl",
            description=(
                "Use this tool to control the robot simulator. Each command requires specific parameters:\n"
                "- move_robot: coordinates=[x, y, z]\n"
                "- pickup_and_place: object_name, target_location=[x, y, z], arm (optional: 'left' or 'right')\n"
                "- spawn_objects: object_choice ('cereal', 'milk', 'spoon', 'bowl'), coordinates=[x, y, z], color (optional)\n"
                "- robot_perceive: perception_area (optional)\n"
                "- look_for_object: object_name\n"
                "- unpack_arms: no parameters required\n"
                "- detect_object: object_type, detection_area (optional)\n"
                "- transport_object: object_name, target_location=[x, y, z], arm (optional: 'left' or 'right')\n\n"
                "IMPORTANT: Always specify parameters explicitly by name in the function call."
            ),
        )

    @staticmethod
    def _get_robot_commands_tool(pycram_api_host, requests_timeout):
        def list_robot_commands():
            api_url = f"{pycram_api_host}/commands"
            response = requests.get(api_url, timeout=requests_timeout)
            if response.status_code == 200:
                return json.dumps(response.json())
            else:
                return f"API error: {response.status_code} - {response.text}"

        return StructuredTool.from_function(
            func=list_robot_commands,
            name="ListRobotCommands",
            description="Use this tool to get a list of all available robot commands",
        )

    def _retrieve_relevant_docs(self, query: str, top_k: int = 3) -> List[str]:
        """Retrieve relevant document chunks for a query."""
        try:
            docs_and_scores = self.vector_store.similarity_search_with_score(query, k=top_k)
            if docs_and_scores:
                # Debug print to verify retrieval
                print(f"Retrieved {len(docs_and_scores)} documents for query: {query}")
                for i, (doc, score) in enumerate(docs_and_scores):
                    print(f"Document {i+1}, Score: {score:.4f}, Content preview: {doc.page_content[:100]}...")
                
                # Fixed to avoid backslash in f-string
                return [f"Document content: {doc.page_content}" for doc, _ in docs_and_scores]
            else:
                print("No relevant documents found for query:", query)
                return ["No relevant document found."]
        except Exception as e:
            print(f"Error retrieving documents: {e}")
            return ["Error retrieving relevant documents."]

    def handle_message(self, message_text: str, base64_images: List[str] = None, base64_images_mimes: List[str] = None) -> str:
        """Handle user message and return response."""
        # Initialize empty lists if None is provided
        base64_images = base64_images or []
        base64_images_mimes = base64_images_mimes or []
        
        image_url = (
            None
            if len(base64_images) == 0
            else f"data:{base64_images_mimes[0]};base64,{base64_images[0]}"
        )

        # Prepare agent input - no context directly here, as we'll use the RAG tool instead
        agent_input = {
            "input": message_text,
            "chat_history": self._chat_history,
        }

        if image_url is not None:
            agent_input["image_url"] = image_url

        # Log that we're processing a message
        print(f"Processing message: {message_text}")
        
        # Run the agent
        result = (
            self._agent_executor_without_image.invoke(agent_input)
            if image_url is None
            else self._agent_executor_with_image.invoke(agent_input)
        )

        # Update chat history
        self._chat_history.extend(
            [
                HumanMessage(content=message_text),
                AIMessage(content=result["output"]),
            ]
        )

        return result["output"]
