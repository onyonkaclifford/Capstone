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

MANIPULATION_CSV = "./tests/data/manipulation.psv"
TEST_REPORT_FILE = "./test_report.json"

with open(MANIPULATION_CSV) as f:
    ALL_TEST_CASES = [i.split("|") for i in f.readlines()[1:]]


def _get_command_test_cases(command):
    return [i for i in ALL_TEST_CASES if i[0].strip() == command]


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
        cls.test_report = []

    @classmethod
    def tearDownClass(cls):
        with open(TEST_REPORT_FILE, "w") as f:
            json.dump(cls.test_report, f, indent=4)

    @staticmethod
    def _are_coordinates_within_range(expected_dict, response_dict, param_name):
        x_range = [float(i) for i in expected_dict["params"][param_name][0].split("-")]
        y_range = [float(i) for i in expected_dict["params"][param_name][1].split("-")]
        z_range = [float(i) for i in expected_dict["params"][param_name][2].split("-")]
        if (
            response_dict["params"][param_name][0] >= x_range[0]
            and response_dict["params"][param_name][0] <= x_range[1]
            and response_dict["params"][param_name][1] >= y_range[0]
            and response_dict["params"][param_name][1] <= y_range[1]
            and response_dict["params"][param_name][2] >= z_range[0]
            and response_dict["params"][param_name][2] <= z_range[1]
        ):
            return True
        else:
            return False

    @staticmethod
    def _manupulation_test_helper(
        functionality_being_tested,
        test_cases,
        similarity_threshold=100,
        check_coordinates_range=False,
        coordinates_name="coordinates",
    ):
        num_of_test_cases = len(test_cases)
        passed = 0
        num_returned_correct_commands = 0
        num_returned_correct_params = 0
        test_cases_results = []
        expected_num_correct_command_params = 0

        for _, user_input, expected_response, asserts in test_cases:
            assert_list = (
                [i.strip().lower() for i in asserts.split(",")]
                if len(asserts.strip()) > 0
                else []
            )
            response = TestRoboCRAM.agent.handle_message(
                user_input.strip(), [], [], print_markers=False
            )

            test_cases_results.append(
                {
                    "user_input": user_input,
                    "expected_output": expected_response,
                    "agent_response": response,
                    "failure_reasons": [],
                    "passed": False,
                }
            )

            to_continue = False
            for i in assert_list:  # User input expected to result in an error
                try:
                    assert i in response.lower()
                except AssertionError:
                    test_cases_results[-1]["failure_reasons"].append(
                        f"Agent response doesn't contain required word, '{i}'"
                    )
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
                    test_cases_results[-1]["failure_reasons"].append(
                        "Agent response is too disimilar to the expected response"
                    )
                    continue
            else:  # User input expected to produce a valid command with correct parameters
                expected_num_correct_command_params += 1
                expected_obj = json.loads(expected_response)
                response_obj = json.loads(response)
                test_cases_results[-1]["expected_output"] = expected_obj
                test_cases_results[-1]["agent_response"] = response_obj

                try:
                    assert response_obj["command"] == expected_obj["command"]
                    num_returned_correct_commands += 1

                    for param_name in expected_obj["params"].keys():
                        if param_name not in response_obj["params"]:
                            test_cases_results[-1]["failure_reasons"].append(
                                f"Agent response doesn't contain required parameter, {param_name}"
                            )
                            continue
                        if param_name == coordinates_name and check_coordinates_range:
                            if not TestRoboCRAM._are_coordinates_within_range(
                                expected_obj, response_obj, coordinates_name
                            ):
                                continue
                        else:
                            assert (
                                expected_obj["params"][param_name]
                                == response_obj["params"][param_name]
                            )

                    num_returned_correct_params += 1
                except AssertionError:
                    test_cases_results[-1]["failure_reasons"].append(
                        "Agent response contains commands or parameters that are unexpected"
                    )
                    continue

            test_cases_results[-1]["passed"] = True
            passed += 1

        TestRoboCRAM.test_report.append(
            {
                "test": functionality_being_tested,
                "num_of_test_cases": num_of_test_cases,
                "passed": passed,
                "num_returned_correct_commands": num_returned_correct_commands,
                "num_returned_correct_params": num_returned_correct_params,
                "expected_num_correct_command_params": expected_num_correct_command_params,
                "test_cases": test_cases_results,
            }
        )

    def test_self_identity(self):
        """
        Does the system know its identity as RoboCRAM?
        """
        user_input = "Who are you"
        expected = "Hello I am RoboCRAM. How can I help?"
        response = TestRoboCRAM.agent.handle_message(
            user_input, [], [], print_markers=False
        )

        try:
            assert "RoboCRAM" in response
            assert Levenshtein.distance(response, expected) < 100
            TestRoboCRAM.test_report.append(
                {
                    "test": "Does the system know its identity as RoboCRAM?",
                    "user_input": user_input,
                    "expected_output": expected,
                    "agent_response": response,
                    "passed": True,
                }
            )
        except AssertionError:
            TestRoboCRAM.test_report.append(
                {
                    "test": "Does the system know its identity as RoboCRAM?",
                    "user_input": user_input,
                    "expected_output": expected,
                    "agent_response": response,
                    "passed": False,
                }
            )

    def test_move_robot(self):
        """
        Can the robot move within its environment?
        """
        TestRoboCRAM._manupulation_test_helper(
            "Can the robot move within its environment?",
            _get_command_test_cases("move_robot"),
        )


if __name__ == "__main__":
    unittest.main()
