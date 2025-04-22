import base64  # Add this import
import json
import logging
import os
import re
import sys
import tempfile  # Add this for better temp file handling

import chainlit as cl
from dotenv import load_dotenv
from PIL import Image

from src import utils
from src.agent import Agent

load_dotenv()

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

with open(SYSTEM_MESSAGE_FILE, "r", encoding="utf-8") as f:
    system_message = f.read()

agent = Agent(

        OPENAI_MODEL,
        TEMPERATURE,
        MAX_TOKENS,
        PYCRAM_API_HOST,
        system_message,
        REQUESTS_TIMEOUT,
        True if VERBOSE == "true" else False,
        handle_parsing_errors=True,
        pdf_directory=RAG_DOCS_DIRECTORY,
)

@cl.on_chat_start
async def on_start():
    await cl.Message(content="I am ready ...").send()


# Your existing code...


# Update the extraction function to find both data URLs and file paths
def extract_image_references(text):
    """Extract both data URLs and file paths from text content"""
    # Data URL pattern
    data_url_pattern = r"(data:image\/[^;]+;base64,[a-zA-Z0-9+/=]+)"
    data_urls = re.findall(data_url_pattern, text)

    # File path pattern - look for image file paths in markdown syntax or JSON
    file_path_pattern = (
        r'!\[.*?\]\((.*?\.png)\)|"image_urls":\s*{\s*"[^"]+"\s*:\s*"([^"]+\.png)"'
    )
    file_paths = []
    for match in re.findall(file_path_pattern, text):
        # Each match could be from different capture groups
        for path in match:
            if path and path.endswith(".png"):
                # Convert backslashes to forward slashes for consistency
                file_paths.append(path.replace("\\", "/"))

    return {"data_urls": data_urls, "file_paths": file_paths}


@cl.on_message
async def main(message: cl.Message):
    """Process incoming messages"""
    try:
        # Extract any images the user might have sent
        images = []
        images_mimes = []

        if message.elements:
            for element in message.elements:
                if hasattr(element, "type") and element.type == "image":
                    img = utils.get_resized_image(
                        Image.open(element.path), IMAGE_MAX_WIDTH
                    )
                    img_ext = utils.get_image_extension(element.name)
                    images.append(utils.get_base64_encoded_image(img, img_ext))
                    images_mimes.append(
                        f"image/{'jpeg' if img_ext == 'jpg' else img_ext}"
                    )

        # Process user message through agent
        agent_response = agent.handle_message(message.content, images, images_mimes)

        # Create initial response message
        response_message = cl.Message(content=agent_response)

        # Look for image paths in the response
        image_paths = []

        # Method 1: Check for Markdown image syntax with local paths
        markdown_images = re.findall(
            r"!\[(.*?)\]\((enhanced_images[/\\][^)]+\.png)\)", agent_response
        )
        for _, img_path in markdown_images:
            image_paths.append(img_path.replace("\\", "/"))

        # Method 2: Look for image_urls or image_path in JSON response
        try:
            json_match = re.search(
                r'({.*?(?:"image_urls"|"image_path").*?})', agent_response
            )
            if json_match:
                json_data = json.loads(json_match.group(1))
                if "image_urls" in json_data and isinstance(
                    json_data["image_urls"], dict
                ):
                    for img_type, img_path in json_data["image_urls"].items():
                        image_paths.append(img_path.replace("\\", "/"))
                elif "image_path" in json_data:
                    image_paths.append(json_data["image_path"].replace("\\", "/"))
        except json.JSONDecodeError:
            pass  # JSON parsing might fail, that's okay

        # Method 3: Direct regex for file paths
        direct_paths = re.findall(r'enhanced_images[/\\][^\s"\']+\.png', agent_response)
        for path in direct_paths:
            if path not in image_paths:
                image_paths.append(path.replace("\\", "/"))

        # Add found images to the message
        for image_path in image_paths:
            if os.path.exists(image_path):
                # Create image element with the file path
                image_element = cl.Image(
                    name=os.path.basename(image_path), path=image_path, display="inline"
                )
                response_message.elements.append(image_element)
                print(f"Added image: {image_path}")

        # Send the message with any found images
        await response_message.send()

    except Exception as e:
        print(f"Error processing message: {str(e)}")
        await cl.Message(content=f"An error occurred: {str(e)}").send()
