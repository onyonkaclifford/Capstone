# import logging
# import os

# import chainlit as cl
# from dotenv import load_dotenv
# from PIL import Image

# import utils
# from agent import Agent

# load_dotenv()

# OPENAI_MODEL = os.getenv("OPENAI_MODEL","gpt-4o-mini")
# TEMPERATURE = float(os.getenv("TEMPERATURE",0.7))
# MAX_TOKENS = int(os.getenv("MAX_TOKENS",10000))
# IMAGE_MAX_WIDTH = int(os.getenv("IMAGE_MAX_WIDTH",480))
# VERBOSE = os.getenv("VERBOSE", "true").strip().lower()

# logger = logging.getLogger("capstone")
# default_temperature = 0.7
# default_verbose = "true"

# if 0.0 > TEMPERATURE or TEMPERATURE > 1.0:
#     logger.warning(
#         f"TEMPERATURE env var only accepts values in [0.0, 1.0] but {TEMPERATURE} is given, "
#         f"defaulting to {default_temperature}"
#     )
#     TEMPERATURE = default_temperature

# if VERBOSE not in ["true", "false"]:
#     logger.warning(
#         f"VERBOSE env var only accepts true or false but {VERBOSE} is given, "
#         f"defaulting to {default_verbose}"
#     )
#     VERBOSE = default_verbose

# agent = Agent(
#     OPENAI_MODEL, TEMPERATURE, MAX_TOKENS, True if VERBOSE == "true" else False
# )


# @cl.on_chat_start
# async def on_start():
#     await cl.Message(content="I am ready ...").send()


# @cl.on_message
# async def on_message(message: cl.Message):
#     images = []
#     images_mimes = []

#     if message.elements:
#         for i in message.elements:
#             if i.type == "image":
#                 img = utils.get_resized_image(Image.open(i.path), IMAGE_MAX_WIDTH)
#                 img_ext = utils.get_image_extension(i.name)
#                 images.append(utils.get_base64_encoded_image(img, img_ext))
#                 images_mimes.append(f"image/{'jpeg' if img_ext == 'jpg' else img_ext}")

#     result = agent.handle_message(message.content, images, images_mimes)
#     await cl.Message(result).send()


import logging
import os
import chainlit as cl
from dotenv import load_dotenv
from PIL import Image
import utils
from agent import Agent

load_dotenv()

# Environment Variables
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
TEMPERATURE = float(os.getenv("TEMPERATURE", 0.7))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", 10000))
IMAGE_MAX_WIDTH = int(os.getenv("IMAGE_MAX_WIDTH", 480))
VERBOSE = os.getenv("VERBOSE", "true").strip().lower()
PDF_DIRECTORY = "docs/"

logger = logging.getLogger("capstone")
default_temperature = 0.7
default_verbose = "true"

if 0.0 > TEMPERATURE or TEMPERATURE > 1.0:
    logger.warning(f"TEMPERATURE out of range. Defaulting to {default_temperature}")
    TEMPERATURE = default_temperature

if VERBOSE not in ["true", "false"]:
    logger.warning(f"VERBOSE value invalid. Defaulting to {default_verbose}")
    VERBOSE = default_verbose

# Initialize Agent with PDF support
agent = Agent(
    OPENAI_MODEL, TEMPERATURE, MAX_TOKENS, True if VERBOSE == "true" else False, PDF_DIRECTORY
)


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

