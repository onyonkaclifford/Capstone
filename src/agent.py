import json

import requests
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import StructuredTool
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

import utils


class Agent:
    def __init__(
        self,
        model,
        temperature,
        max_tokens,
        pycram_api_host,
        system_message_text,
        requests_timeout,
        verbose=True,
        handle_parsing_errors=True,
    ):
        self._chat_history = []

        tools = [
            Agent._get_hello_tool(),
            Agent._get_robot_tool(pycram_api_host, requests_timeout),
            Agent._get_robot_commands_tool(pycram_api_host, requests_timeout),
        ]
        llm = ChatOpenAI(model=model, temperature=temperature, max_tokens=max_tokens)

        self._agent_executor_with_image = AgentExecutor(
            agent=create_openai_tools_agent(
                llm,
                tools,
                Agent._get_prompt_template(system_message_text, with_image=True),
            ),
            tools=tools,
            verbose=verbose,
            handle_parsing_errors=handle_parsing_errors,
        )
        self._agent_executor_without_image = AgentExecutor(
            agent=create_openai_tools_agent(
                llm,
                tools,
                Agent._get_prompt_template(system_message_text, with_image=False),
            ),
            tools=tools,
            verbose=verbose,
            handle_parsing_errors=handle_parsing_errors,
        )

    @staticmethod
    def _get_prompt_template(system_message_text, with_image=False):
        return ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=system_message_text),
                MessagesPlaceholder(variable_name="chat_history"),
                (
                    "human",
                    (
                        [
                            {"type": "text", "text": "{input}"},
                            {"type": "image_url", "image_url": "{image_url}"},
                        ]
                        if with_image
                        else [{"type": "text", "text": "{input}"}]
                    ),
                ),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

    @staticmethod
    def _get_hello_tool():
        return StructuredTool.from_function(
            func=lambda: "Hello I am RoboCRAM. How can I help?",
            name="Hello",
            description="Use this tool when asked who you are or about your identity",
        )

    @staticmethod
    def _get_robot_tool(pycram_api_host, requests_timeout):
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
            api_url = f"{pycram_api_host}/execute"
            kwargs |= {
                "coordinates": coordinates,
                "object_name": object_name,
                "target_location": target_location,
                "arm": arm,
                "object_choice": object_choice,
                "color": color,
                "perception_area": perception_area,
                "object_type": object_type,
                "detection_area": detection_area,
            }
            required_command_parameters = {
                "move_robot": ["coordinates"],
                "pickup_and_place": ["object_name", "target_location"],
                "transport_object": ["object_name", "target_location"],
                "spawn_objects": ["object_choice", "coordinates"],
                "look_for_object": ["object_name"],
                "detect_object": ["object_type"],
            }

            if command is None:
                return "Please specify a robot command"

            # [kwargs.pop(k) for k, v in kwargs.items() if v is None]
            kwargs = {k: v for k, v in kwargs.items() if v is not None}
            if command in required_command_parameters:
                missing_params = [param for param in required_command_parameters[command] 
                                if param not in kwargs]
                if missing_params:
                    return (
                        f"ERROR: {command} command requires these missing parameters: {', '.join(missing_params)}. "
                        "Make sure to pass them explicitly by name. "
                        "When passing coordinates, use the format 'coordinates=[x, y, z]'."
                    )
            
            if "coordinates" in kwargs and (
                not isinstance(kwargs["coordinates"], list)
                or not len(kwargs["coordinates"]) == 3
            ):
                return "ERROR: coordinates must be a list of exactly 3 values [x, y, z]"
            if "arm" in kwargs and kwargs["arm"] not in ["left", "right"]:
                return "ERROR: arm takes the values: 'left' or 'right']"

            coordinates = (
                [
                    float(kwargs["coordinates"][0]),
                    float(kwargs["coordinates"][1]),
                    float(kwargs["coordinates"][2]),
                ]
                if "coordinates" in kwargs
                else None
            )
            command_params = utils.RobotToolDict(
                "coordinates",
                {
                    "unpack_arms": [],
                    "move_robot": [(coordinates, "coordinates")],
                    "look_for_object": [(kwargs, "object_name")],
                    "robot_perceive": [(kwargs, "perception_area")],
                    "detect_object": [
                        (kwargs, "object_type"),
                        (kwargs, "detection_area"),
                    ],
                    "pickup_and_place": [
                        (kwargs, "object_name"),
                        (coordinates, "target_location"),
                        (kwargs, "arm"),
                    ],
                    "transport_object": [
                        (kwargs, "object_name"),
                        (coordinates, "coordinates"),
                        (kwargs, "arm"),
                    ],
                    "spawn_objects": [
                        (kwargs, "object_choice"),
                        (coordinates, "coordinates"),
                        (kwargs, "color"),
                    ],
                },
            )

            if command not in command_params:
                raise ValueError(f"ERROR: Unknown command '{command}'")

            response = requests.post(
                api_url,
                json={"command": command, "params": command_params[command]},
                timeout=requests_timeout,
            )

            if response.status_code == 200:
                result = response.json()
                return json.dumps(result)
            else:
                return f"API error: {response.status_code} - {response.text}"

        return StructuredTool.from_function(
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

    @staticmethod
    def _get_robot_commands_tool(pycram_api_host, requests_timeout):
        def list_robot_commands():
            api_url = f"{pycram_api_host}/commands"
            response = requests.get(api_url, timeout=requests_timeout)
            if response.status_code == 200:
                return json.dumps(response.json())
            else:
                return f"API error: {response.status_code} - {response.text}"

        return StructuredTool.from_function(
            func=list_robot_commands,
            name="ListRobotCommands",
            description="Use this tool to get a list of all available robot commands",
        )

    def handle_message(self, message_text, base64_images, base64_images_mimes):
        image_url = (
            None
            if len(base64_images) == 0
            else f"data:{base64_images_mimes[0]};base64,{base64_images[0]}"
        )

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
