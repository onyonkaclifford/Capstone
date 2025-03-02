from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad.openai_tools import (
    format_to_openai_tool_messages,
)
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI


class Agent:
    def __init__(self, model, temperature, max_tokens, verbose):
        self._chat_history = []
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
                | ChatOpenAI(
                    model=model, temperature=temperature, max_tokens=max_tokens
                )
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
                | ChatOpenAI(
                    model=model, temperature=temperature, max_tokens=max_tokens
                )
                | OpenAIToolsAgentOutputParser()
            ),
            tools=[],
            verbose=verbose,
        )

    @staticmethod
    def _get_prompt_template(with_image=True):
        return ChatPromptTemplate.from_messages(
            [
                ("system", "You are a question answering system"),
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

    def handle_message(self, message_text, base64_images, base64_images_mimes):
        image_url = (
            None
            if len(base64_images) == 0
            else f"data:{base64_images_mimes[0]};base64,{base64_images[0]}"
        )
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
        self._chat_history.extend(
            [
                HumanMessage(content=message_text),
                AIMessage(content=result["output"]),
            ]
        )

        return result["output"]
