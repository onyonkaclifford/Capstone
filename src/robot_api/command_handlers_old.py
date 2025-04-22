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


class TransportObjectHandler(RobotCommandHandler):
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

        return {"command": "transport_object", "params": api_params}


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


class LookForObjectHandler(RobotCommandHandler):
    def __init__(self):
        super().__init__(required_params=["object_name"])

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "command": "look_for_object",
            "params": {"object_name": params["object_name"]},
        }


class DetectObjectHandler(RobotCommandHandler):
    def __init__(self):
        super().__init__(required_params=["object_type"])

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        api_params = {"object_type": params["object_type"]}

        if "detection_area" in params:
            api_params["detection_area"] = params["detection_area"]

        return {"command": "detect_object", "params": api_params}


class RobotPerceiveHandler(RobotCommandHandler):
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        api_params = {}

        if "perception_area" in params:
            api_params["perception_area"] = params["perception_area"]

        return {"command": "robot_perceive", "params": api_params}


class UnpackArmsHandler(RobotCommandHandler):
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"command": "unpack_arms", "params": {}}


class MoveTorsoHandler(RobotCommandHandler):
    def validate_params(self, params: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        if "position" in params and params["position"].lower() not in ["low", "high"]:
            return False, "position must be 'low' or 'high'"
        return True, None

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        api_params = {}

        if "position" in params:
            api_params["position"] = params["position"]

        return {"command": "move_torso", "params": api_params}


class ParkArmsHandler(RobotCommandHandler):
    def validate_params(self, params: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        if "arm" in params and params["arm"].lower() not in ["left", "right", "both"]:
            return False, "arm must be 'left', 'right', or 'both'"
        return True, None

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        api_params = {}

        if "arm" in params:
            api_params["arm"] = params["arm"]

        return {"command": "park_arms", "params": api_params}


class MoveAndRotateHandler(RobotCommandHandler):
    def validate_params(self, params: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        if "location" in params:
            location = params.get("location")
            if not isinstance(location, list) or len(location) != 3:
                return False, "location must be a list of exactly 3 values [x, y, z]"

            try:
                # Convert to float
                params["location"] = [float(c) for c in location]
            except (ValueError, TypeError):
                return False, "location must contain numeric values"

        if "angle" in params:
            try:
                params["angle"] = float(params["angle"])
            except (ValueError, TypeError):
                return False, "angle must be a numeric value"

        return True, None

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        api_params = {}

        if "location" in params:
            api_params["location"] = params["location"]

        if "angle" in params:
            api_params["angle"] = params["angle"]

        return {"command": "move_and_rotate", "params": api_params}


class GetCameraImagesHandler(RobotCommandHandler):
    def validate_params(self, params: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        if "target_distance" in params:
            try:
                params["target_distance"] = float(params["target_distance"])
            except (ValueError, TypeError):
                return False, "target_distance must be a numeric value"
        return True, None

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        api_params = {}

        if "target_distance" in params:
            api_params["target_distance"] = params["target_distance"]

        return {"command": "get_camera_images", "params": api_params}


class GetEnhancedCameraImagesHandler(RobotCommandHandler):
    def validate_params(self, params: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        if "target_distance" in params:
            try:
                params["target_distance"] = float(params["target_distance"])
            except (ValueError, TypeError):
                return False, "target_distance must be a numeric value"
        return True, None

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        api_params = {}

        if "target_distance" in params:
            api_params["target_distance"] = params["target_distance"]

        return {"command": "get_enhanced_camera_images", "params": api_params}


class ListRobotCommandsHandler(RobotCommandHandler):
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"command": "list_commands", "params": {}}


# New handlers for missing APIs
class SpawnInAreaHandler(RobotCommandHandler):
    def __init__(self):
        super().__init__(required_params=["object_choice", "surface_name"])

    def validate_params(self, params: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        valid, error_msg = super().validate_params(params)
        if not valid:
            return False, error_msg
        if "offset" in params:
            offset = params["offset"]
            if not isinstance(offset, list) or len(offset) != 3:
                return False, "offset must be a list of exactly 3 values [dx, dy, dz]"
            try:
                params["offset"] = [float(c) for c in offset]
            except (ValueError, TypeError):
                return False, "offset must contain numeric values"
        return True, None

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        api_params = {
            "object_choice": params["object_choice"],
            "surface_name": params["surface_name"],
        }
        if "offset" in params:
            api_params["offset"] = params["offset"]
        if "color" in params:
            api_params["color"] = params["color"]
        return {"command": "spawn_in_area", "params": api_params}


class GetPlacementSurfacesHandler(RobotCommandHandler):
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"command": "get_placement_surfaces", "params": {}}


class PickAndPlaceOnSurfaceHandler(RobotCommandHandler):
    def __init__(self):
        super().__init__(required_params=["object_name", "surface_name"])

    def validate_params(self, params: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        valid, error_msg = super().validate_params(params)
        primary_surfaces_list = [
            "sink_area_surface",
            "kitchen_island_surface",
            "kitchen_island_stove",
            "table_area_main",
            "oven_area_area",
        ]
        secondary_surfaces_list = [
            "sink_area_sink",
            "oven_area_oven_door",
            "fridge_area",
        ]
        if not valid:
            return False, error_msg

        # Validate surface_name is acceptable
        surface_name = params.get("surface_name")
        if surface_name not in primary_surfaces_list and surface_name not in secondary_surfaces_list:
            return False, f"Invalid surface_name: {surface_name}"

        # Handle offset: convert a list of values into offset_x and offset_y, or use defaults
        if "offset" in params:
            offset = params["offset"]
            # Check if offset is a list and has at least 2 elements
            if not isinstance(offset, list) or len(offset) < 2:
                return False, "offset must be a list with at least 2 values [dx, dy]"
            
            try:
                # Take just the first two elements for x and y
                offset_x = float(offset[0])
                offset_y = float(offset[1])
                params["offset_x"] = offset_x
                params["offset_y"] = offset_y
            except (ValueError, TypeError, IndexError):
                return False, "offset must contain numeric values"
        else:
            params["offset_x"] = 0.1
            params["offset_y"] = 0.1

        # Validate 'arm' if provided, or set default to 'right'
        if "arm" in params:
            if params["arm"] not in ["left", "right"]:
                return False, "arm must be 'left' or 'right'"
        else:
            params["arm"] = "right"

        return True, None

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        api_params = {
            "object_name": params["object_name"],
            "surface_name": params["surface_name"],
            "offset_x": params["offset_x"],
            "offset_y": params["offset_y"],
            "arm": params["arm"],
        }
        return {"command": "pick_and_place_on_surface", "params": api_params}


class GetRobotPoseHandler(RobotCommandHandler):
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"command": "get_robot_pose", "params": {}}


class CalculateRelativeDistancesHandler(RobotCommandHandler):
    def __init__(self):
        super().__init__(required_params=["object_a", "object_b"])

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "command": "calculate_relative_distances",
            "params": {"object_a": params["object_a"], "object_b": params["object_b"]},
        }


class CalculateObjectDistancesHandler(RobotCommandHandler):
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        api_params = {}
        if "source_object_name" in params:
            api_params["source_object_name"] = params["source_object_name"]
        if "target_object_names" in params:
            api_params["target_object_names"] = params["target_object_names"]
        if "exclude_object_names" in params:
            api_params["exclude_object_names"] = params["exclude_object_names"]
        return {"command": "calculate_object_distances", "params": api_params}
    
class GetWorldObjectsHandler(RobotCommandHandler):
    """Handler for retrieving objects in the world with optional filtering"""
    
    def validate_params(self, params: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        # Validate exclude_types if provided
        if "exclude_types" in params and not isinstance(params["exclude_types"], list):
            return False, "exclude_types must be a list of strings"
            
        # Validate obj_type if provided
        if "obj_type" in params and not isinstance(params["obj_type"], str):
            return False, "obj_type must be a string"
            
        # Validate area if provided
        if "area" in params and not isinstance(params["area"], str):
            return False, "area must be a string"
            
        return True, None
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        api_params = {}
        
        # Add parameters if provided
        if "exclude_types" in params:
            api_params["exclude_types"] = params["exclude_types"]
            
        if "obj_type" in params:
            api_params["obj_type"] = params["obj_type"]
            
        if "area" in params:
            api_params["area"] = params["area"]
            
        return {
            "command": "get_world_objects",
            "params": api_params
        }



# Handler mapping for all robot commands
handler_mapping = {
    "move_robot": MoveRobotHandler(),
    "pickup_and_place": PickupAndPlaceHandler(),
    "transport_object": TransportObjectHandler(),
    "spawn_objects": SpawnObjectsHandler(),
    "spawn_in_area": SpawnInAreaHandler(),
    "look_for_object": LookForObjectHandler(),
    "detect_object": DetectObjectHandler(),
    "robot_perceive": RobotPerceiveHandler(),
    "get_placement_surfaces": GetPlacementSurfacesHandler(),
    "pick_and_place_on_surface": PickAndPlaceOnSurfaceHandler(),
    "move_torso": MoveTorsoHandler(),
    "park_arms": ParkArmsHandler(),
    "unpack_arms": UnpackArmsHandler(),
    "move_and_rotate": MoveAndRotateHandler(),
    "get_camera_images": GetCameraImagesHandler(),
    "get_enhanced_camera_images": GetEnhancedCameraImagesHandler(),
    "list_robot_commands": ListRobotCommandsHandler(),
    "get_robot_pose": GetRobotPoseHandler(),
    "calculate_relative_distances": CalculateRelativeDistancesHandler(),
    "calculate_object_distances": CalculateObjectDistancesHandler(),
    "get_world_objects": GetWorldObjectsHandler(),
}
