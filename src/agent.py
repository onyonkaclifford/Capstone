from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


class Agent:
    def __init__(self):
        self.chat_history = []

    @staticmethod
    def _get_prompt_template():
        return ChatPromptTemplate.from_messages([
            ("human", "Hello"),
            ("ai", "Hello too")
        ])

    @staticmethod
    def get_agent_executor(model, temperature):
        return AgentExecutor(
            agent=(
                {
                    "input": lambda x: x["input"],
                    "agent_scratchpad": lambda x: format_to_openai_tool_messages(
                        x["intermediate_steps"]
                    ),
                    "chat_history": lambda x: x["chat_history"],
                } |
                Agent._get_prompt_template() |
                ChatOpenAI(model=model, temperature=temperature) |
                OpenAIToolsAgentOutputParser()
            ),
            tools=[],
            verbose=True
        )

    def handle_message(self, message, cl_user_session):
        user_message = message.content.lower()
        result = cl_user_session.invoke({"input": user_message, "chat_history": self.chat_history})
        self.chat_history.extend([
            HumanMessage(content=user_message),
            AIMessage(content=result["output"]),
        ])

        return result
