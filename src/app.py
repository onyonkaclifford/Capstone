import logging
import os

import chainlit as cl
from dotenv import load_dotenv
from PIL import Image

import utils
from agent import Agent
import re
import sys
import base64

import logging
import os
import base64  # Add this import
import re
import tempfile  # Add this for better temp file handling

import chainlit as cl
from dotenv import load_dotenv
from PIL import Image

import utils
from agent import Agent

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

with open(SYSTEM_MESSAGE_FILE, "r") as f:
    system_message = f.read()

agent = Agent(
    OPENAI_MODEL,
    TEMPERATURE,
    MAX_TOKENS,
    PYCRAM_API_HOST,
    system_message,
    REQUESTS_TIMEOUT,
    True if VERBOSE == "true" else False,
)

# Add a function to extract image data URLs from text
def extract_data_urls(text):
    """Extract data URLs from text content"""
    # Pattern to match data URLs in Markdown image syntax or in a JSON string
    pattern = r'(data:image\/[^;]+;base64,[a-zA-Z0-9+/=]+)'
    return re.findall(pattern, text)

@cl.on_chat_start
async def on_start():
    await cl.Message(content="I am ready ...").send()


@cl.on_message
async def main(message: cl.Message):
    """Process incoming messages"""
    try:
        # Log the start of processing
        print("Processing message:", message.content)
        
        # Extract any images the user might have sent
        images = []
        images_mimes = []

        if message.elements:
            for element in message.elements:
                if hasattr(element, 'type') and element.type == "image":
                    img = utils.get_resized_image(Image.open(element.path), IMAGE_MAX_WIDTH)
                    img_ext = utils.get_image_extension(element.name)
                    images.append(utils.get_base64_encoded_image(img, img_ext))
                    images_mimes.append(f"image/{'jpeg' if img_ext == 'jpg' else img_ext}")
        
        # Process user message through agent
        agent_response = agent.handle_message(
            message.content, 
            images, 
            images_mimes
        )
        
        # Check if response contains image data URLs
        data_urls = extract_data_urls(agent_response)
        print(f"Found {len(data_urls)} image data URLs in response")
        
        # Create response message with original text first
        response_message = cl.Message(content=agent_response)
        
        # Process any found data URLs
        if data_urls:
            cleaned_content = agent_response
            
            for i, data_url in enumerate(data_urls):
                try:
                    # Extract the base64 part
                    if "base64," in data_url:
                        base64_part = data_url.split("base64,")[1]
                        
                        # Create a temporary file with proper extension
                        temp_dir = tempfile.gettempdir()
                        temp_filename = f"temp_image_{i}.png"
                        temp_path = os.path.join(temp_dir, temp_filename)
                        
                        print(f"Creating temp file at: {temp_path}")
                        
                        # Decode and save the image
                        with open(temp_path, "wb") as img_file:
                            img_file.write(base64.b64decode(base64_part))
                        
                        # Add image to the message as an element
                        image_element = cl.Image(path=temp_path, display="inline")
                        response_message.elements.append(image_element)
                        
                        # Clean the response text to remove embedded images
                        for pattern in [
                            f"!\\[.*?\\]\\({re.escape(data_url)}\\)",  # Markdown image syntax with any alt text
                            re.escape(data_url)  # Just the URL itself
                        ]:
                            cleaned_content = re.sub(pattern, "", cleaned_content)
                
                except Exception as e:
                    print(f"Error processing image {i}: {str(e)}")
            
            # Update with cleaned content
            response_message.content = cleaned_content.strip()
        
        # Send the message
        print("Sending response message")
        await response_message.send()
        print("Response sent successfully")
        
    except Exception as e:
        print(f"Error processing message: {str(e)}")
        await cl.Message(content=f"An error occurred: {str(e)}").send()
