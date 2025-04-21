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
            "coordinates",
            "object_name",
            "target_location",
            "arm",
            "object_choice",
            "color",
            "perception_area",
            "object_type",
            "detection_area",
        ]:
            if param in locals_dict and locals_dict[param] is not None:
                params[param] = locals_dict[param]

        # Add any additional kwargs
        params.update(kwargs)

        # Call the API class
        return robot_api.execute_command(command=command, **params)

    # Read the tool description from the txt file
    import os

    tool_desc_path = os.path.join(os.path.dirname(__file__), "robochat_tool_api.txt")
    with open(tool_desc_path, "r", encoding="utf-8") as f:
        description = f.read()

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
