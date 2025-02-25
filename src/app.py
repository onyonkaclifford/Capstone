import os

import chainlit as cl
from dotenv import load_dotenv

from agent import Agent


load_dotenv()
OPENAI_MODEL = os.getenv("OPENAI_MODEL")
agent = Agent()


@cl.on_chat_start
async def on_start():
    cl.user_session.set("llm_chain", Agent.get_agent_executor(model=OPENAI_MODEL, temperature=0.7))
    await cl.Message(content="I am ready ...").send()


@cl.on_message
async def on_message(message: cl.Message):
    result = agent.handle_message(message, cl.user_session.get("llm_chain"))
    await cl.Message(result["output"]).send()
