import base64
import json
import os
from datetime import datetime
from typing import Any, Dict

import requests

from .command_handlers import handler_mapping


class RobotAPINoExec:
    """Main class for interacting with the Robot API without executing commands"""

    def __init__(self):
        self.handlers = handler_mapping
        with open(
            os.path.join(os.path.dirname(__file__), "command_descriptions.json"), "r"
        ) as f:
            self.command_descriptions = json.load(f)

    def execute_command(self, command: str = None, **params) -> str:
        """
        Execute a robot command with the given parameters

        Args:
            command: The name of the command to execute
            **params: Command-specific parameters

        Returns:
            JSON string response from the API
        """
        if command is None:
            return "Please specify a robot command"

        if command not in self.handlers:
            return f"ERROR: Unknown command '{command}'"

        handler = self.handlers[command]
        valid, error_msg = handler.validate_params(params)

        if not valid:
            return f"ERROR: {error_msg}"

        return json.dumps(handler.execute(params))

    def get_commands_list(self) -> str:
        """Get a list of all available commands with descriptions"""
        command_info = []
        for command, handler in self.handlers.items():
            required = getattr(handler, "required_params", [])
            description = self.command_descriptions.get(
                command, "No description available"
            )
            command_info.append(
                {
                    "name": command,
                    "description": description,
                    "required_parameters": required,
                }
            )

        return json.dumps({"commands": command_info})
