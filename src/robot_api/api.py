"""
Main RobotAPI class for interacting with the robot simulator
"""

import base64
import json

# orientation = euler_to_quaternion(0, 0, 120)
import os
from datetime import datetime
from typing import Any, Dict

import requests

from .command_handlers import (
    DetectObjectHandler,
    GetCameraImagesHandler,
    GetEnhancedCameraImagesHandler,
    ListRobotCommandsHandler,
    LookForObjectHandler,
    MoveAndRotateHandler,
    MoveRobotHandler,
    MoveTorsoHandler,
    ParkArmsHandler,
    PickupAndPlaceHandler,
    RobotPerceiveHandler,
    SpawnObjectsHandler,
    TransportObjectHandler,
    UnpackArmsHandler,
)


class RobotAPI:
    """Main class for interacting with the Robot API"""

    def __init__(self, api_host: str, timeout: int = 30):
        self.api_host = api_host
        self.timeout = timeout

        # Register command handlers
        self.handlers = {
            "move_robot": MoveRobotHandler(),
            "pickup_and_place": PickupAndPlaceHandler(),
            "transport_object": TransportObjectHandler(),
            "spawn_objects": SpawnObjectsHandler(),
            "look_for_object": LookForObjectHandler(),
            "detect_object": DetectObjectHandler(),
            "robot_perceive": RobotPerceiveHandler(),
            "unpack_arms": UnpackArmsHandler(),
            "move_torso": MoveTorsoHandler(),
            "park_arms": ParkArmsHandler(),
            "move_and_rotate": MoveAndRotateHandler(),
            "get_camera_images": GetCameraImagesHandler(),
            "get_enhanced_camera_images": GetEnhancedCameraImagesHandler(),
            "list_robot_commands": ListRobotCommandsHandler(),
        }

        # Command descriptions for documentation
        self.command_descriptions = {
            "move_robot": "Move the robot to specified coordinates",
            "pickup_and_place": "Pick up an object and place it at a target location",
            "transport_object": "Transport an object to a target location",
            "spawn_objects": "Create an object in the simulation environment",
            "look_for_object": "Make the robot look at the specified object",
            "detect_object": "Detect an object in the robot's environment",
            "robot_perceive": "Make the robot perceive its environment",
            "unpack_arms": "Unpack the robot's arms from their stowed position",
            "move_torso": "Move the robot's torso to a specified position",
            "park_arms": "Move the robot's arm(s) to the pre-defined parking position",
            "move_and_rotate": "Move the robot to a location and/or rotate it",
            "get_camera_images": "Capture images from the robot's camera",
            "get_enhanced_camera_images": "Capture enhanced visualization of images",
            "list_robot_commands": "List all available robot commands",
        }

    def execute_command(self, command: str = None, **params) -> str:
        """
        Execute a robot command with the given parameters

        Args:
            command: The name of the command to execute
            **params: Command-specific parameters

        Returns:
            JSON string response from the API
        """
        # Check if command is provided
        if command is None:
            return "Please specify a robot command"

        # Check if command exists
        if command not in self.handlers:
            return f"ERROR: Unknown command '{command}'"

        # Get the handler for this command
        handler = self.handlers[command]

        # Validate parameters
        valid, error_msg = handler.validate_params(params)
        if not valid:
            return f"ERROR: {error_msg}"

        # Execute the command
        try:
            request_data = handler.execute(params)
            return self._make_api_call(request_data["command"], request_data["params"])
        except Exception as e:
            return f"ERROR: Command execution failed: {str(e)}"

    def _make_api_call(self, command: str, params: Dict[str, Any]) -> str:
        """Make the actual API call"""
        print(
            f"Making API call to {self.api_host} with command: {command} and params: {params}"
        )
        api_url = f"{self.api_host}/execute"
        try:
            response = requests.post(
                api_url,
                json={"command": command, "params": params},
                timeout=self.timeout,
            )

            # Process response
            if response.status_code == 200:
                result = response.json()
                # print(f"API response: {result}")
                # check if the command was get_camera_images or get_enhanced_camera_images
                if command in ["get_camera_images", "get_enhanced_camera_images"]:
                    try:
                        image_dir, saved_files = RobotAPI.save_images_from_response(
                            result
                        )
                        result["image_dir"] = image_dir

                        # Store only the file paths - no need for data URLs
                        if "images" in result and saved_files:
                            image_types = list(result["images"].keys())
                            result["image_urls"] = {}

                            # Create a mapping between image types and their file paths
                            for i, img_type in enumerate(image_types):
                                if i < len(saved_files):
                                    result["image_urls"][img_type] = saved_files[i]

                            # Remove the original base64 data to reduce payload size
                            del result["images"]

                        # Keep the first image path for backward compatibility
                        if saved_files:
                            result["image_path"] = saved_files[0]

                    except Exception as e:
                        return f"ERROR: Failed to save or process images: {str(e)}"

                return json.dumps(result)
            else:
                return f"API error: {response.status_code} - {response.text}"
        except requests.exceptions.RequestException as e:
            return f"Request error: {str(e)}"

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

    @staticmethod
    def save_images_from_response(
        result: dict, image_dir: str = "enhanced_images"
    ) -> (str, list):
        """
        Given an API response dict with structure:
        {
            "status": "success",
            "images": {
            "color_image": "<base64…>",
            "depth_image": "<base64…>",
            …
            },
            "message": "…"
        }
        this function:
        1. Verifies success.
        2. Creates `image_dir` if needed.
        3. Saves each image under a timestamped filename.
        4. Returns (directory_path, [list of saved file paths]).

        Args:
            result:    The dict returned by response.json().
            image_dir: Directory to save images into.

        Returns:
            A tuple (image_dir, saved_files), where:
            - image_dir is the directory you passed in (created if needed).
            - saved_files is a list of the full file paths you wrote.
        """
        # # 1) Check status
        # if result.get("status") != "success":
        #     raise ValueError(f"API error: {result.get('message', 'unknown error')}")

        # 2) Make directory
        if not os.path.exists(image_dir):
            os.makedirs(image_dir, exist_ok=True)

        # 3) Timestamp for filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        saved_files = []
        for img_type, img_b64 in result.get("images", {}).items():
            # Decode base64
            img_bytes = base64.b64decode(img_b64)

            # Build filename
            filename = os.path.join(image_dir, f"{timestamp}_{img_type}.png")

            # Write to disk
            with open(filename, "wb") as f:
                f.write(img_bytes)

            saved_files.append(filename)
            print(f"Saved {img_type} to {filename}")

        return image_dir, saved_files
