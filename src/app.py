import base64
import mimetypes
from io import BytesIO
import logging
import os

import chainlit as cl
from dotenv import load_dotenv
from PIL import Image

from agent import Agent


load_dotenv()

OPENAI_MODEL = os.getenv("OPENAI_MODEL")
TEMPERATURE = float(os.getenv("TEMPERATURE"))
MAX_TOKENS=int(os.getenv("MAX_TOKENS"))
IMAGE_RESIZE_WIDTH=int(os.getenv("IMAGE_RESIZE_WIDTH"))
VERBOSE = os.getenv("VERBOSE").lower()

logger = logging.getLogger("capstone")
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

agent = Agent(OPENAI_MODEL, TEMPERATURE, MAX_TOKENS, True if VERBOSE == "true" else False)


@cl.on_chat_start
async def on_start():
    await cl.Message(content="I am ready ...").send()


@cl.on_message
async def on_message(message: cl.Message):
    images = []

    if message.elements:
        for i in message.elements:
            if i.type == "file" and i.mime.startswith("image/"):
                img = Image.open(BytesIO(i.content))
                img_ext = mimetypes.guess_extension(i.mime)[1:].upper()
                img_w, img_h = img.size()
                resize_factor = IMAGE_RESIZE_WIDTH / img_w
                img = img.resize((IMAGE_RESIZE_WIDTH, int(img_h * resize_factor)))
                buffer = BytesIO()
                img.save(buffer, img_ext)
                images.append(base64.b64decode(buffer.getvalue()).decode("UTF-8"))

    result = agent.handle_message(message.content, images)
    await cl.Message(result).send()
