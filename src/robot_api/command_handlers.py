"""
Command handler classes for robot API commands
"""

from typing import Any, Dict, List, Optional, Tuple


class RobotCommandHandler:
    """Base class for command handlers"""

    def __init__(self, required_params: List[str] = None):
        self.required_params = required_params or []

    def validate_params(self, params: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate that all required parameters are present"""
        missing = [p for p in self.required_params if p not in params]
        if missing:
            return False, f"Missing required parameters: {', '.join(missing)}"
        return True, None

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the command with the given parameters"""
        raise NotImplementedError("Subclasses must implement execute method")


class MoveRobotHandler(RobotCommandHandler):
    def __init__(self):
        super().__init__(required_params=["coordinates"])

    def validate_params(self, params: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        valid, error_msg = super().validate_params(params)
        if not valid:
            return False, error_msg

        # Additional validation
        coordinates = params.get("coordinates")
        if not isinstance(coordinates, list) or len(coordinates) != 3:
            return False, "coordinates must be a list of exactly 3 values [x, y, z]"

        try:
            # Convert to float
            params["coordinates"] = [float(c) for c in coordinates]
        except (ValueError, TypeError):
            return False, "coordinates must contain numeric values"

        return True, None

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "command": "move_robot",
            "params": {"coordinates": params["coordinates"]},
        }


class PickupAndPlaceHandler(RobotCommandHandler):
    def __init__(self):
        super().__init__(required_params=["object_name", "target_location"])

    def validate_params(self, params: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        valid, error_msg = super().validate_params(params)
        if not valid:
            return False, error_msg

        # Validate target_location format
        target_location = params.get("target_location")
        if not isinstance(target_location, list) or len(target_location) != 3:
            return False, "target_location must be a list of exactly 3 values [x, y, z]"

        try:
            # Convert to float
            params["target_location"] = [float(c) for c in target_location]
        except (ValueError, TypeError):
            return False, "target_location must contain numeric values"

        # Validate arm if provided
        if "arm" in params and params["arm"] not in ["left", "right"]:
            return False, "arm must be 'left' or 'right'"

        return True, None

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        api_params = {
            "object_name": params["object_name"],
            "target_location": params["target_location"],
        }

        if "arm" in params:
            api_params["arm"] = params["arm"]

        return {"command": "pickup_and_place", "params": api_params}


class SpawnObjectsHandler(RobotCommandHandler):
    def __init__(self):
        super().__init__(required_params=["object_choice", "coordinates"])

    def validate_params(self, params: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        valid, error_msg = super().validate_params(params)
        if not valid:
            return False, error_msg

        # Validate coordinates format
        coordinates = params.get("coordinates")
        if not isinstance(coordinates, list) or len(coordinates) != 3:
            return False, "coordinates must be a list of exactly 3 values [x, y, z]"

        try:
            # Convert to float
            params["coordinates"] = [float(c) for c in coordinates]
        except (ValueError, TypeError):
            return False, "coordinates must contain numeric values"

        return True, None

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        api_params = {
            "object_choice": params["object_choice"],
            "coordinates": params["coordinates"],
        }

        if "color" in params:
            api_params["color"] = params["color"]

        return {"command": "spawn_objects", "params": api_params}


class GetPlacementSurfacesHandler(RobotCommandHandler):
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"command": "get_placement_surfaces", "params": {}}


class SpawnInAreaHandler(RobotCommandHandler):
    def __init__(self):
        super().__init__(required_params=["object_choice", "surface_name"])

    def validate_params(self, params: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        valid, error_msg = super().validate_params(params)
        if not valid:
            return False, error_msg
        
        # Handle offset_x and offset_y
        if "offset_x" in params:
            try:
                params["offset_x"] = float(params["offset_x"])
            except (ValueError, TypeError):
                return False, "offset_x must be a numeric value"
                
        if "offset_y" in params:
            try:
                params["offset_y"] = float(params["offset_y"])
            except (ValueError, TypeError):
                return False, "offset_y must be a numeric value"
                
        return True, None

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        api_params = {
            "object_choice": params["object_choice"],
            "surface_name": params["surface_name"],
        }
        
        # Add optional parameters if provided
        if "offset_x" in params:
            api_params["offset_x"] = params["offset_x"]
            
        if "offset_y" in params:
            api_params["offset_y"] = params["offset_y"]
            
        if "color" in params:
            api_params["color"] = params["color"]
            
        if "name" in params:
            api_params["name"] = params["name"]
            
        return {"command": "spawn_in_area", "params": api_params}


class PickAndPlaceOnSurfaceHandler(RobotCommandHandler):
    def __init__(self):
        super().__init__(required_params=["object_name", "surface_name"])

    def validate_params(self, params: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        valid, error_msg = super().validate_params(params)
        if not valid:
            return False, error_msg

        # Handle offset_x and offset_y
        if "offset_x" in params:
            try:
                params["offset_x"] = float(params["offset_x"])
            except (ValueError, TypeError):
                return False, "offset_x must be a numeric value"
                
        if "offset_y" in params:
            try:
                params["offset_y"] = float(params["offset_y"])
            except (ValueError, TypeError):
                return False, "offset_y must be a numeric value"
                
        # Validate 'arm' if provided
        if "arm" in params and params["arm"] not in ["left", "right"]:
            return False, "arm must be 'left' or 'right'"
            
        return True, None

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        api_params = {
            "object_name": params["object_name"],
            "surface_name": params["surface_name"],
        }
        
        # Add optional parameters if provided
        if "offset_x" in params:
            api_params["offset_x"] = params["offset_x"]
            
        if "offset_y" in params:
            api_params["offset_y"] = params["offset_y"]
            
        if "arm" in params:
            api_params["arm"] = params["arm"]
            
        return {"command": "pick_and_place_on_surface", "params": api_params}

class GetWorldObjectsHandler(RobotCommandHandler):
    """Handler for retrieving objects in the world with optional filtering"""
    
    def validate_params(self, params: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        # Validate exclude_types if provided
        if "exclude_types" in params:
            # Handle string representation of a list
            if isinstance(params["exclude_types"], str):
                try:
                    # Try to convert from string representation to a list
                    import ast
                    params["exclude_types"] = ast.literal_eval(params["exclude_types"])
                except:
                    return False, "exclude_types must be a valid list of strings"
            
            if not isinstance(params["exclude_types"], list):
                return False, "exclude_types must be a list of strings"
            
        # Validate obj_type if provided
        if "obj_type" in params and not isinstance(params["obj_type"], str):
            return False, "obj_type must be a string"
            
        # Validate area if provided
        if "area" in params and not isinstance(params["area"], str):
            return False, "area must be a string"
            
        return True, None
        
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Initialize with default exclusions
        api_params = {
            "exclude_types": ["floor", "wall", "ceiling", "ground", "kitchen", "apartment", "pr2"]
        }
        
        # Override defaults if explicitly provided in params
        if "exclude_types" in params:
            api_params["exclude_types"] = params["exclude_types"]
            
        if "obj_type" in params:
            api_params["obj_type"] = params["obj_type"]
            
        if "area" in params:
            api_params["area"] = params["area"]
            
        # # Log the execution for debugging
        # if os.environ.get("VERBOSE", "False").lower() == "true":
        #     print(f"GetWorldObjectsHandler executing with params: {api_params}")
            
        return {
            "command": "get_world_objects",
            "params": api_params
        }

# class GetWorldObjectsHandler(RobotCommandHandler):
#     """Handler for retrieving objects in the world with optional filtering"""
    
#     def validate_params(self, params: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
#         # Validate exclude_types if provided
#         if "exclude_types" in params and not isinstance(params["exclude_types"], list):
#             return False, "exclude_types must be a list of strings"
            
#         # Validate obj_type if provided
#         if "obj_type" in params and not isinstance(params["obj_type"], str):
#             return False, "obj_type must be a string"
            
#         # Validate area if provided
#         if "area" in params and not isinstance(params["area"], str):
#             return False, "area must be a string"
            
#         return True, None
    
#     def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
#         # Initialize with default exclusions
#         api_params = {
#             "exclude_types": ["floor", "wall", "ceiling", "ground", "kitchen", "apartment", "pr2"]
#         }
        
#         # Override defaults if explicitly provided in params
#         if "exclude_types" in params:
#             api_params["exclude_types"] = params["exclude_types"]
            
#         if "obj_type" in params:
#             api_params["obj_type"] = params["obj_type"]
            
#         if "area" in params:
#             api_params["area"] = params["area"]
            
#         return {
#             "command": "get_world_objects",
#             "params": api_params
#         }


class ListRobotCommandsHandler(RobotCommandHandler):
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"command": "list_robot_commands", "params": {}}


# Handler mapping for all robot commands - LEANER VERSION
handler_mapping = {
    "move_robot": MoveRobotHandler(),
    "pickup_and_place": PickupAndPlaceHandler(),   
    "spawn_objects": SpawnObjectsHandler(),
    "spawn_in_area": SpawnInAreaHandler(),      
    "get_placement_surfaces": GetPlacementSurfacesHandler(),
    "pick_and_place_on_surface": PickAndPlaceOnSurfaceHandler(),    
    "get_world_objects": GetWorldObjectsHandler(),
    "list_robot_commands": ListRobotCommandsHandler(),
}
