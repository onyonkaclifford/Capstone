import json
import math

import requests
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.agents.format_scratchpad.openai_tools import (
    format_to_openai_tool_messages,
)
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain.tools import StructuredTool
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

# Import the process_user_request function from run.py
# from run import process_user_request


def hello_tool():
    """Tool that responds with identity information."""
    return "Hello I am robocram. How can I help"


def circle_api_tool(
    operation: str = None,
    radius: float = None,
    diameter: float = None,
    area: float = None,
    circumference: float = None,
):
    """
    Access the Circle API to perform circle-related calculations.

    Args:
        operation (str): The operation to perform ('area', 'circumference', 'radius', or 'diameter')
        radius (float, optional): The radius of the circle
        diameter (float, optional): The diameter of the circle
        area (float, optional): The area of the circle
        circumference (float, optional): The circumference of the circle

    Returns:
        str: Result of the circle calculation from the API
    """
    if operation is None:
        return "Please specify an operation: 'area', 'circumference', 'radius', or 'diameter'"

    # Build API parameters
    params = {"operation": operation}
    if radius is not None:
        params["radius"] = radius
    if diameter is not None:
        params["diameter"] = diameter
    if area is not None:
        params["area"] = area
    if circumference is not None:
        params["circumference"] = circumference

    # API endpoint - adjust URL based on where your API is running
    api_url = "http://localhost:8002/circle"  # Default to localhost:8002 per the run_api.py config

    try:
        # Make the API request
        response = requests.get(api_url, params=params)

        # Check if request was successful
        if response.status_code == 200:
            result = response.json()
            return result.get("result", "API returned no result")
        else:
            return f"API error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error accessing Circle API: {str(e)}"


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
    """
    Access the PyCRAM API to control a robot simulator.

    Args:
        command (str): The command to execute (e.g., 'move_robot', 'pickup_and_place', etc.)
        coordinates (list, optional): List of [x, y, z] coordinates
        object_name (str, optional): Name of the object to manipulate
        target_location (list, optional): List of [x, y, z] coordinates for target location
        arm (str, optional): Which arm to use ('left' or 'right')
        object_choice (str, optional): Type of object to spawn
        color (str, optional): Color of the object
        perception_area (str, optional): Area to perceive
        object_type (str, optional): Type of object to detect
        detection_area (str, optional): Area to detect in
        **kwargs: Additional parameters needed for the specific command

    Returns:
        str: Result of the robot command execution
    """
    if command is None:
        return "Please specify a robot command"

    # API endpoint
    api_url = "http://192.168.1.64:8001/execute"

    # Initialize params dictionary
    params = {}

    # Convert explicitly provided parameters to kwargs for uniform handling
    if coordinates is not None:
        kwargs["coordinates"] = coordinates
    if object_name is not None:
        kwargs["object_name"] = object_name
    if target_location is not None:
        kwargs["target_location"] = target_location
    if arm is not None:
        kwargs["arm"] = arm
    if object_choice is not None:
        kwargs["object_choice"] = object_choice
    if color is not None:
        kwargs["color"] = color
    if perception_area is not None:
        kwargs["perception_area"] = perception_area
    if object_type is not None:
        kwargs["object_type"] = object_type
    if detection_area is not None:
        kwargs["detection_area"] = detection_area

    # lets print the kwargs and the command
    print(f"Command: {command}")
    print(f"Kwargs: {kwargs}")

    # Additional validation to catch common errors
    if command == "move_robot" and "coordinates" not in kwargs:
        return "ERROR: move_robot command requires 'coordinates' parameter. Make sure to pass it as coordinates=[x, y, z]"

    if command in ["pickup_and_place", "transport_object"]:
        missing_params = []
        if "object_name" not in kwargs:
            missing_params.append("object_name")
        if "target_location" not in kwargs:
            missing_params.append("target_location")
        if missing_params:
            return f"ERROR: {command} command requires these missing parameters: {', '.join(missing_params)}. Make sure to pass them explicitly by name."

    if command == "spawn_objects":
        missing_params = []
        if "object_choice" not in kwargs:
            missing_params.append("object_choice")
        if "coordinates" not in kwargs:
            missing_params.append("coordinates")
        if missing_params:
            return f"ERROR: spawn_objects command requires these missing parameters: {', '.join(missing_params)}. Make sure to pass them explicitly by name."

    if command == "look_for_object" and "object_name" not in kwargs:
        return "ERROR: look_for_object command requires 'object_name' parameter. Make sure to pass it explicitly by name."

    if command == "detect_object" and "object_type" not in kwargs:
        return "ERROR: detect_object command requires 'object_type' parameter. Make sure to pass it explicitly by name."

    # Command-specific parameter handling
    if command == "move_robot":
        # Handle move_robot command (requires coordinates)
        if "coordinates" not in kwargs:
            return "Error: 'move_robot' command requires 'coordinates' parameter"

        coords = kwargs["coordinates"]
        if isinstance(coords, list) and len(coords) == 3:
            params["coordinates"] = [
                float(coords[0]),
                float(coords[1]),
                float(coords[2]),
            ]
        else:
            return "Error: coordinates must be a list of exactly 3 values [x, y, z]"

    elif command == "pickup_and_place":
        # Handle pickup_and_place command (requires object_name, target_location, optional arm)
        if "object_name" not in kwargs:
            return "Error: 'pickup_and_place' command requires 'object_name' parameter"
        if "target_location" not in kwargs:
            return (
                "Error: 'pickup_and_place' command requires 'target_location' parameter"
            )

        params["object_name"] = kwargs["object_name"]

        coords = kwargs["target_location"]
        if isinstance(coords, list) and len(coords) == 3:
            params["target_location"] = [
                float(coords[0]),
                float(coords[1]),
                float(coords[2]),
            ]
        else:
            return "Error: target_location must be a list of exactly 3 values [x, y, z]"

        # Add arm parameter if provided
        if "arm" in kwargs and kwargs["arm"]:
            if kwargs["arm"] in ["left", "right", None]:
                params["arm"] = kwargs["arm"]
            else:
                params["arm"] = (
                    None  # return "Error: 'arm' must be 'left', 'right', or null"
                )

    elif command == "spawn_objects":
        # Handle spawn_objects command (requires object_choice, coordinates, optional color)
        if "object_choice" not in kwargs:
            return "Error: 'spawn_objects' command requires 'object_choice' parameter"
        if "coordinates" not in kwargs:
            return "Error: 'spawn_objects' command requires 'coordinates' parameter"

        params["object_choice"] = kwargs["object_choice"]

        coords = kwargs["coordinates"]
        if isinstance(coords, list) and len(coords) == 3:
            params["coordinates"] = [
                float(coords[0]),
                float(coords[1]),
                float(coords[2]),
            ]
        else:
            return "Error: coordinates must be a list of exactly 3 values [x, y, z]"

        # Add color if provided
        if "color" in kwargs and kwargs["color"]:
            params["color"] = kwargs["color"]

    elif command == "robot_perceive":
        # Handle robot_perceive command (optional perception_area)
        if "perception_area" in kwargs:
            params["perception_area"] = kwargs["perception_area"]

    elif command == "look_for_object":
        # Handle look_for_object command (requires object_name)
        if "object_name" not in kwargs:
            return "Error: 'look_for_object' command requires 'object_name' parameter"

        params["object_name"] = kwargs["object_name"]

    elif command == "unpack_arms":
        # Handle unpack_arms command (no parameters required)
        pass

    elif command == "detect_object":
        # Handle detect_object command (requires object_type, optional detection_area)
        if "object_type" not in kwargs:
            return "Error: 'detect_object' command requires 'object_type' parameter"

        params["object_type"] = kwargs["object_type"]

        if "detection_area" in kwargs:
            params["detection_area"] = kwargs["detection_area"]

    elif command == "transport_object":
        # Handle transport_object command (requires object_name, target_location, optional arm)
        if "object_name" not in kwargs:
            return "Error: 'transport_object' command requires 'object_name' parameter"
        if "target_location" not in kwargs:
            return (
                "Error: 'transport_object' command requires 'target_location' parameter"
            )

        params["object_name"] = kwargs["object_name"]

        coords = kwargs["target_location"]
        if isinstance(coords, list) and len(coords) == 3:
            params["target_location"] = [
                float(coords[0]),
                float(coords[1]),
                float(coords[2]),
            ]
        else:
            return "Error: target_location must be a list of exactly 3 values [x, y, z]"

        # Add arm parameter if provided
        if "arm" in kwargs and kwargs["arm"]:
            if kwargs["arm"] in ["left", "right"]:
                params["arm"] = kwargs["arm"]
            else:
                return "Error: 'arm' must be 'left' or 'right'"

    else:
        return f"Error: Unknown command '{command}'"

    # Prepare request payload
    payload = {"command": command, "params": params}

    try:
        # Make the API request
        response = requests.post(api_url, json=payload)

        # Check if request was successful
        if response.status_code == 200:
            result = response.json()
            return json.dumps(result, indent=2)  # Return formatted JSON response
        else:
            return f"API error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error accessing Robot API: {str(e)}"


def list_robot_commands():
    """List all available robot commands from the PyCRAM API."""
    api_url = "http://192.168.1.64:8001/commands"

    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            return json.dumps(response.json(), indent=2)
        else:
            return f"API error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error accessing Robot API commands: {str(e)}"


# Create structured tools
hello_tool_structured = StructuredTool.from_function(
    func=hello_tool,
    name="Hello",
    description="Use this tool when asked who you are or about your identity",
)

circle_tool_structured = StructuredTool.from_function(
    func=circle_api_tool,
    name="CircleCalculator",
    description="Use this tool for ANY circle-related calculations. Specify an operation ('area', 'circumference', 'radius', or 'diameter') and provide the necessary parameters.",
)

robot_tool_structured = StructuredTool.from_function(
    func=robot_api_tool,
    name="RobotControl",
    description=(
        "Use this tool to control the robot simulator. Each command requires specific parameters:\n"
        "- move_robot: coordinates=[x, y, z]\n"
        "- pickup_and_place: object_name, target_location=[x, y, z], arm (optional: 'left' or 'right')\n"
        "- spawn_objects: object_choice ('cereal', 'milk', 'spoon', 'bowl'), coordinates=[x, y, z], color (optional)\n"
        "- robot_perceive: perception_area (optional)\n"
        "- look_for_object: object_name\n"
        "- unpack_arms: no parameters required\n"
        "- detect_object: object_type, detection_area (optional)\n"
        "- transport_object: object_name, target_location=[x, y, z], arm (optional: 'left' or 'right')\n\n"
        "IMPORTANT: Always specify parameters explicitly by name in the function call. For example, use:\n"
        "command='move_robot', coordinates=[x, y, z]\n"
        "and NOT just command='move_robot' with coordinates in a separate parameter."
    ),
)

robot_commands_tool = StructuredTool.from_function(
    func=list_robot_commands,
    name="ListRobotCommands",
    description="Use this tool to get a list of all available robot commands.",
)


class Agent:
    def __init__(self, model, temperature, max_tokens, verbose):
        self._chat_history = []
        # Define tools
        self._tools = [
            hello_tool_structured,
            circle_tool_structured,
            robot_tool_structured,
            robot_commands_tool,
        ]

        # Define system message with explicit tool usage examples
        system_message = SystemMessage(
            content=(
                "You are RoboCram, an advanced AI assistant specialized in controlling robots and performing calculations. "
                "Your primary function is to interpret user requests and execute them by calling the appropriate tools. "
                "IMPORTANT: You MUST use available tools instead of answering from memory when applicable. "
                "\n\n1. CIRCLE CALCULATIONS: For ANY questions about circles (area, circumference, radius, diameter), use the CircleCalculator tool."
                "\n\n2. ROBOT CONTROL: Map natural language requests to specific robot commands:"
                "\n- For movement requests: Use command='move_robot' with coordinates=[x, y, z]"
                "\n- For object manipulation: Use command='pickup_and_place' with object_name, target_location=[x, y, z], and arm"
                "\n- For creating objects: Use command='spawn_objects' with object_choice, coordinates=[x, y, z], and color"
                "\n- For perception: Use command='robot_perceive' with perception_area"
                "\n- For object detection: Use command='detect_object' with object_type"
                "\n- For object transport: Use command='transport_object' with object_name, target_location=[x, y, z], and arm"
                "\n- For searching objects: Use command='look_for_object' with object_name"
                "\n- For unpacking robot's arms: Use command='unpack_arms' with no parameters"
                "\n\nIMPORTANT: Always pass parameters with explicit names. For example:"
                "\n- CORRECT: command='move_robot', coordinates=[2, 3, 0]"
                "\n- INCORRECT: command='move_robot', [2, 3, 0]"
                "\n\nCOMMAND MAPPING EXAMPLES:"
                "\n- 'Move the robot to position 2, 3, 0' → command='move_robot', coordinates=[2, 3, 0]"
                "\n- 'Pick up the milk and place it at 1, 2, 0.8' → command='pickup_and_place', object_name='milk', target_location=[1, 2, 0.8]"
                "\n- 'Create a red bowl at position 1.4, 1, 0.95' → command='spawn_objects', object_choice='bowl', coordinates=[1.4, 1, 0.95], color='red'"
                "\n- 'What objects are on the table?' → command='robot_perceive', perception_area='table'"
                "\n- 'Find the cereal box' → command='look_for_object', object_name='cereal'"
                "\n- 'Use your right arm to move the spoon to 1.5, 1, 0.9' → command='transport_object', object_name='spoon', target_location=[1.5, 1, 0.9], arm='right'"
                "\n\nPARAMETER GUIDELINES:"
                "\n- coordinates: Always provide as a list of 3 values [x, y, z]"
                "\n- object_name: Use the exact name of objects ('milk', 'cereal', 'spoon', 'bowl', etc.)"
                "\n- object_choice: Limited to 'cereal', 'milk', 'spoon', 'bowl' for spawn_objects"
                "\n- arm: Use 'left', 'right', or omit for automatic selection"
                "\n- color: Available options are 'red', 'blue', 'green', 'yellow', 'white', 'black'"
                "\n\nINFERENCE RULES:"
                "\n- Any request mentioning 'pick', 'grab', 'take', or 'get' + placing = 'pickup_and_place'"
                "\n- Any request mentioning 'move' or 'go' + robot = 'move_robot'"
                "\n- Any request mentioning 'move' + object name = 'transport_object'"
                "\n- Any request mentioning 'create', 'spawn', 'add' + object = 'spawn_objects'"
                "\n- Any request mentioning 'look', 'find', 'locate' + object = 'look_for_object'"
                "\n- Any request mentioning 'perceive', 'what', 'scan' + area = 'robot_perceive'"
                "\n\nDo not say phrases like 'I will calculate' or 'Let me use the tool' - just USE the tool directly."
            )
        )

        # Create LLM
        self._llm = ChatOpenAI(
            model=model, temperature=temperature, max_tokens=max_tokens
        )

        # Create prompts
        prompt_with_image = ChatPromptTemplate.from_messages(
            [
                system_message,
                MessagesPlaceholder(variable_name="chat_history"),
                (
                    "human",
                    [
                        {"type": "text", "text": "{input}"},
                        {"type": "image_url", "image_url": "{image_url}"},
                    ],
                ),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        prompt_without_image = ChatPromptTemplate.from_messages(
            [
                system_message,
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        # Create agents
        agent_with_image = create_openai_tools_agent(
            self._llm, self._tools, prompt_with_image
        )
        agent_without_image = create_openai_tools_agent(
            self._llm, self._tools, prompt_without_image
        )

        # Create executors
        self._agent_executor_with_image = AgentExecutor(
            agent=agent_with_image,
            tools=self._tools,
            verbose=verbose,
            handle_parsing_errors=True,
        )

        self._agent_executor_without_image = AgentExecutor(
            agent=agent_without_image,
            tools=self._tools,
            verbose=verbose,
            handle_parsing_errors=True,
        )

    def handle_message(self, message_text, base64_images, base64_images_mimes):
        image_url = (
            None
            if len(base64_images) == 0
            else f"data:{base64_images_mimes[0]};base64,{base64_images[0]}"
        )

        try:
            result = (
                self._agent_executor_without_image.invoke(
                    {"input": message_text, "chat_history": self._chat_history}
                )
                if image_url is None
                else self._agent_executor_with_image.invoke(
                    {
                        "input": message_text,
                        "image_url": image_url,
                        "chat_history": self._chat_history,
                    }
                )
            )

            # Ensure we have output
            if "output" in result:
                self._chat_history.extend(
                    [
                        HumanMessage(content=message_text),
                        AIMessage(content=result["output"]),
                    ]
                )
                return result["output"]
            else:
                return "An error occurred while processing your request."

        except Exception as e:
            return f"An error occurred: {str(e)}"
