"""
Factory functions for creating LangChain tools from the RobotAPI
"""

from langchain.tools import StructuredTool

from .api import RobotAPI
from .api_no_exec import RobotAPINoExec
from .evaluation_tracker import finalize_record, set_model_output


def create_robot_api_tool(pycram_api_host, requests_timeout, skip_execution: bool):
    """
    Create a structured tool for LangChain from the RobotAPI class

    Args:
        pycram_api_host: Host URL for the robot API
        requests_timeout: Timeout for API requests in seconds

    Returns:
        StructuredTool instance for use with LangChain
    """
    # Create an instance of our RobotAPI class
    if skip_execution:
        robot_api = RobotAPINoExec()
    else:
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
        surface_name: str = None,
        offset: list = None,
        offset_x: float = None,
        offset_y: float = None,
        **kwargs,
    ):
        print("\n==== ROBOT API TOOL CALLED ====") if not skip_execution else "No print"
        print(f"Command: {command}") if not skip_execution else "No print"
        (
            print(
                f"Parameters: {', '.join([f'{k}={v}' for k, v in locals().items() if k != 'command' and k != 'kwargs' and v is not None])}"
            )
            if not skip_execution
            else "No print"
        )

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
            "surface_name",
            "offset",
            "offset_x",
            "offset_y",
        ]:
            if param in locals_dict and locals_dict[param] is not None:
                params[param] = locals_dict[param]

        # Add any additional kwargs
        params.update(kwargs)

        # Track the model output for evaluation
        set_model_output(command, params, verbose=not skip_execution)
        (
            print("Model output recorded in evaluation tracker")
            if not skip_execution
            else "No print"
        )

        # Call the API class
        print(f"Calling robot_api.execute_command with command={command}")
        result = robot_api.execute_command(command=command, **params)

        # Finalize the evaluation record
        print("Finalizing evaluation record") if not skip_execution else "No print"
        finalize_record(verbose=not skip_execution)
        print("Evaluation record finalized") if not skip_execution else "No print"

        return result

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


def create_robot_commands_tool(pycram_api_host, requests_timeout, skip_execution: bool):
    """
    Create a structured tool for listing robot commands

    Args:
        pycram_api_host: Host URL for the robot API
        requests_timeout: Timeout for API requests in seconds

    Returns:
        StructuredTool instance for use with LangChain
    """
    # Create an instance of our RobotAPI class
    if skip_execution:
        robot_api = RobotAPINoExec()
    else:
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
