"""
Factory functions for creating LangChain tools from the RobotAPI
"""

from langchain.tools import StructuredTool

from .api import RobotAPI

def create_robot_api_tool(pycram_api_host, requests_timeout):
    """
    Create a structured tool for LangChain from the RobotAPI class
    
    Args:
        pycram_api_host: Host URL for the robot API
        requests_timeout: Timeout for API requests in seconds
        
    Returns:
        StructuredTool instance for use with LangChain
    """
    # Create an instance of our RobotAPI class
    robot_api = RobotAPI(pycram_api_host, requests_timeout)
    
    # Create the adapter function for LangChain
    def robot_api_tool(
        command: str = None,
        coordinates: list = None,
        object_name: str = None,
        target_location: list = None,
        arm: str = None,
        object_choice: str = None,
        color: str = None,
        perception_area: str = None,
        object_type: str = None,
        detection_area: str = None,
        **kwargs,
    ):
        # Collect non-None parameters
        params = {}
        locals_dict = locals()
        for param in [
            "coordinates", "object_name", "target_location", "arm",
            "object_choice", "color", "perception_area", "object_type",
            "detection_area"
        ]:
            if param in locals_dict and locals_dict[param] is not None:
                params[param] = locals_dict[param]
        
        # Add any additional kwargs
        params.update(kwargs)
        
        # Call the API class
        return robot_api.execute_command(command=command, **params)
    
    # Create the description for the tool
    description = (
        "Use this tool to control the robot simulator. Each command requires specific parameters:\n"
        "- move_robot: coordinates=[x, y, z]\n"
        "- pickup_and_place: object_name, target_location=[x, y, z], arm (optional: 'left' or 'right')\n"
        "- spawn_objects: object_choice ('cereal', 'milk', 'spoon', 'bowl'), coordinates=[x, y, z], color (optional)\n"
        "- robot_perceive: perception_area (optional)\n"
        "- look_for_object: object_name\n"
        "- unpack_arms: no parameters required\n"
        "- detect_object: object_type, detection_area (optional)\n"
        "- transport_object: object_name, target_location=[x, y, z], arm (optional: 'left' or 'right')\n"
        "- move_torso: position (optional: 'low' or 'high')\n"
        "- park_arms: arm (optional: 'left', 'right', 'both')\n"
        "- move_and_rotate: location=[x, y, z] (optional), angle (optional)\n"
        "- get_camera_images: target_distance (optional)\n"
        "- get_enhanced_camera_images: target_distance (optional)\n\n"
        "IMPORTANT: Always specify parameters explicitly by name in the function call."
    )
    
    # Return the StructuredTool
    return StructuredTool.from_function(
        func=robot_api_tool,
        name="RobotControl",
        description=description,
    )


def create_robot_commands_tool(pycram_api_host, requests_timeout):
    """
    Create a structured tool for listing robot commands
    
    Args:
        pycram_api_host: Host URL for the robot API
        requests_timeout: Timeout for API requests in seconds
        
    Returns:
        StructuredTool instance for use with LangChain
    """
    # Create an instance of our RobotAPI class
    robot_api = RobotAPI(pycram_api_host, requests_timeout)
    
    # Create the function for the tool
    def list_robot_commands():
        return robot_api.get_commands_list()
    
    # Return the StructuredTool
    return StructuredTool.from_function(
        func=list_robot_commands,
        name="ListRobotCommands",
        description="Use this tool to get a list of all available robot commands",
    )