"""
Main RobotAPI class for interacting with the robot simulator
"""

import json
import requests
from typing import Dict, Any

from .command_handlers import (
    MoveRobotHandler, PickupAndPlaceHandler, TransportObjectHandler,
    SpawnObjectsHandler, LookForObjectHandler, DetectObjectHandler,
    RobotPerceiveHandler, UnpackArmsHandler, MoveTorsoHandler,
    ParkArmsHandler, MoveAndRotateHandler, GetCameraImagesHandler,
    GetEnhancedCameraImagesHandler, ListRobotCommandsHandler
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
            "list_robot_commands": "List all available robot commands"
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
                return json.dumps(result)
            else:
                return f"API error: {response.status_code} - {response.text}"
        except requests.exceptions.RequestException as e:
            return f"Request error: {str(e)}"
    
    def get_commands_list(self) -> str:
        """Get a list of all available commands with descriptions"""
        command_info = []
        for command, handler in self.handlers.items():
            required = getattr(handler, 'required_params', [])
            description = self.command_descriptions.get(command, "No description available")
            command_info.append({
                "name": command,
                "description": description,
                "required_parameters": required
            })
        
        return json.dumps({"commands": command_info})