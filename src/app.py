
import logging
import os

import chainlit as cl
from dotenv import load_dotenv
from PIL import Image

import utils
from agent import Agent

load_dotenv()

OPENAI_MODEL = os.getenv("OPENAI_MODEL")
TEMPERATURE = float(os.getenv("TEMPERATURE"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS"))
IMAGE_MAX_WIDTH = int(os.getenv("IMAGE_MAX_WIDTH"))
VERBOSE = os.getenv("VERBOSE").lower()
LOGGER_NAME = os.getenv("LOGGER_NAME").lower()
PYCRAM_API_HOST = os.getenv("PYCRAM_API_HOST")
SYSTEM_MESSAGE_FILE = os.getenv("SYSTEM_MESSAGE_FILE")
REQUESTS_TIMEOUT = int(os.getenv("REQUESTS_TIMEOUT"))
RAG_DOCS_DIRECTORY ="docs/" #os.getenv("RAG_DOCS_DIRECTORY", "docs/")


logger = logging.getLogger(LOGGER_NAME)
default_temperature = 0.7
default_verbose = "true"

if 0.0 > TEMPERATURE or TEMPERATURE > 1.0:
    logger.warning(
        f"TEMPERATURE env var only accepts values in [0.0, 1.0] but {TEMPERATURE} is given, "
        f"defaulting to {default_temperature}"
    )
    TEMPERATURE = default_temperature

if VERBOSE not in ["true", "false"]:
    logger.warning(
        f"VERBOSE env var only accepts true or false but {VERBOSE} is given, "
        f"defaulting to {default_verbose}"
    )
    VERBOSE = default_verbose

with open(SYSTEM_MESSAGE_FILE, "r") as f:
    system_message = f.read()
# Before creating the agent, ensure the directory exists
if not os.path.exists(RAG_DOCS_DIRECTORY):
    os.makedirs(RAG_DOCS_DIRECTORY)

try:
    agent = Agent(
        OPENAI_MODEL,
        TEMPERATURE,
        MAX_TOKENS,
        PYCRAM_API_HOST,
        system_message,
        REQUESTS_TIMEOUT,
        True if VERBOSE == "true" else False,
        handle_parsing_errors=True,
        pdf_directory=RAG_DOCS_DIRECTORY
    )
except Exception as e:
    logger.error(f"Failed to create agent: {str(e)}")
    raise
@cl.on_chat_start
async def on_start():
    await cl.Message(content="I am ready ...").send()


@cl.on_message
async def on_message(message: cl.Message):
    images = []
    images_mimes = []

    if message.elements:
        for i in message.elements:
            if i.type == "image":
                img = utils.get_resized_image(Image.open(i.path), IMAGE_MAX_WIDTH)
                img_ext = utils.get_image_extension(i.name)
                images.append(utils.get_base64_encoded_image(img, img_ext))
                images_mimes.append(f"image/{'jpeg' if img_ext == 'jpg' else img_ext}")

    result = agent.handle_message(message.content, images, images_mimes)
    await cl.Message(result).send()

