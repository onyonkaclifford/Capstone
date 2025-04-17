import json

# Standard library imports
import requests

# Third-party imports
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import StructuredTool
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

# Local imports
from robot_api import create_robot_api_tool, create_robot_commands_tool


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
    ):
        self._chat_history = []

        tools = [
            Agent._get_hello_tool(),
            create_robot_api_tool(pycram_api_host, requests_timeout),
            create_robot_commands_tool(pycram_api_host, requests_timeout),
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

    def handle_message(self, message_text, base64_images, base64_images_mimes):
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
        print("")
        print("=====================================")
        print("Processing new input message...")
        print(f"Received message: {message_text}")

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
