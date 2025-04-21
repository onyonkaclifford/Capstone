import json
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

MOVE_ROBOT_CSV = "./tests/data/move_robot.csv"
TEST_REPORT_FILE = "./test_report.txt"


class TestRoboCRAM(unittest.TestCase):
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
        cls.test_report_text = ""

    @classmethod
    def tearDownClass(cls):
        with open(TEST_REPORT_FILE, "w") as f:
            f.write(cls.test_report_text)

    @staticmethod
    def _manupulation_test_helper(
        functionality_being_tested, test_cases_file, similarity_threshold=100
    ):
        with open(test_cases_file) as f:
            test_cases = [i.split("|") for i in f.readlines()[1:]]

        num_of_test_cases = len(test_cases)
        passed = 0

        for user_input, expected_response, asserts in test_cases:
            assert_list = [i.strip().lower() for i in asserts.split(",")]
            response = TestRoboCRAM.agent.handle_message(
                user_input.strip(), [], [], print_markers=False
            )
            to_continue = False

            for i in assert_list:  # User input expected to result in an error
                try:
                    assert i in response.lower()
                except AssertionError:
                    to_continue = True
                    break

            if to_continue:
                continue

            if len(assert_list) > 0:  # User input expected to result in an error
                try:
                    assert (
                        Levenshtein.distance(
                            response.lower(), expected_response.lower()
                        )
                        < similarity_threshold
                    )
                except AssertionError:
                    continue
            else:  # User input expected to produce a valid command with correct parameters
                response_obj = json.loads(response)
                expected_obj = json.loads(expected_response)
                try:
                    assert response_obj["command"] == expected_obj["command"]
                    assert response_obj["coordinates"] == expected_obj["coordinates"]
                except AssertionError:
                    continue

            passed += 1

        TestRoboCRAM.test_report_text += f"{functionality_being_tested} {passed}/{num_of_test_cases} test cases passed\n"

    def test_self_identity(self):
        """
        Does the system know its identity as RoboCRAM?
        """
        response = TestRoboCRAM.agent.handle_message(
            "Who are you", [], [], print_markers=False
        )
        expected = "Hello I am RoboCRAM. How can I help?"

        try:
            assert "RoboCRAM" in response
            assert Levenshtein.distance(response, expected) < 100
            TestRoboCRAM.test_report_text += (
                "Does the system know its identity as RoboCRAM? Yes\n"
            )
        except AssertionError:
            TestRoboCRAM.test_report_text += (
                "Does the system know its identity as RoboCRAM? No\n"
            )

    def test_move_robot(self):
        """
        Can the robot move within its environment?
        """
        TestRoboCRAM._manupulation_test_helper(
            "Can the robot move within its environment?", MOVE_ROBOT_CSV
        )


if __name__ == "__main__":
    unittest.main()
