import logging
import os
import sys
import unittest

import Levenshtein
from dotenv import load_dotenv

from src.agent import Agent

load_dotenv()

OPENAI_MODEL = os.getenv("OPENAI_MODEL")
TEMPERATURE = float(os.getenv("TEMPERATURE"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS"))
LOGGER_NAME = os.getenv("LOGGER_NAME").lower()
SYSTEM_MESSAGE_FILE = os.getenv("SYSTEM_MESSAGE_FILE")

logger = logging.getLogger(LOGGER_NAME)

if 0.0 > TEMPERATURE or TEMPERATURE > 1.0:
    logger.error(
        f"TEMPERATURE env var only accepts values in the interval [0.0, 1.0], but '{TEMPERATURE}' is given"
    )
    sys.exit(1)

with open(SYSTEM_MESSAGE_FILE, "r", encoding="utf-8") as f:
    system_message = f.read()


class TestStringMethods(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.agent = Agent(
            OPENAI_MODEL,
            TEMPERATURE,
            MAX_TOKENS,
            pycram_api_host="Not used",
            system_message_text=system_message,
            requests_timeout=-1,
            verbose=False,
            skip_execution=True,
        )

    def test_self_identity(self):
        """
        Does the system know its identity as RoboCRAM?
        """
        response = self.agent.handle_message("Who are you", [], [])
        expected = "Hello I am RoboCRAM. How can I help?"
        self.assertTrue("RoboCRAM" in response)
        self.assertLessEqual(Levenshtein.distance(response, expected), 100)


if __name__ == "__main__":
    unittest.main()
