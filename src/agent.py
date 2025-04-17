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
        # Returns a simple tool that greets the user.
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
            # Check if command is provided
            if command is None:
                return "Please specify a robot command"
                
            # Collect all parameters into kwargs for easier handling
            all_params = {
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
            
            # Add any additional kwargs
            all_params.update(kwargs)
            
            # Remove None values
            all_params = {k: v for k, v in all_params.items() if v is not None}
            
            # Define required parameters for each command
            required_params = {
                "move_robot": ["coordinates"],
                "pickup_and_place": ["object_name", "target_location"],
                "transport_object": ["object_name", "target_location"],
                "spawn_objects": ["object_choice", "coordinates"],
                "look_for_object": ["object_name"],
                "detect_object": ["object_type"],
                "unpack_arms": [],  # No required params
            }
            
            # Check if command is valid
            if command not in required_params:
                return f"ERROR: Unknown command '{command}'"
                
            # Check for required parameters
            missing = [
                p for p in required_params[command] 
                if p not in all_params
            ]
            if missing:
                return (
                    f"ERROR: {command} command requires these missing parameters: {', '.join(missing)}. "
                    "Make sure to pass them explicitly by name."
                )
                
            # Validate parameter types and values
            if "coordinates" in all_params:
                if not isinstance(all_params["coordinates"], list) or len(all_params["coordinates"]) != 3:
                    return "ERROR: coordinates must be a list of exactly 3 values [x, y, z]"
                # Convert to float
                all_params["coordinates"] = [float(c) for c in all_params["coordinates"]]
                
            if "arm" in all_params and all_params["arm"] not in ["left", "right"]:
                return "ERROR: arm takes the values: 'left' or 'right']"
                
            # Prepare params for specific commands
            api_params = {}
            
            if command == "move_robot":
                api_params["coordinates"] = all_params["coordinates"]
                
            elif command == "pickup_and_place":
                api_params["object_name"] = all_params["object_name"]
                api_params["target_location"] = all_params["target_location"]
                if "arm" in all_params:
                    api_params["arm"] = all_params["arm"]
                    
            elif command == "transport_object":
                api_params["object_name"] = all_params["object_name"]
                api_params["target_location"] = all_params["target_location"]
                if "arm" in all_params:
                    api_params["arm"] = all_params["arm"]
                    
            elif command == "spawn_objects":
                api_params["object_choice"] = all_params["object_choice"]
                api_params["coordinates"] = all_params["coordinates"]
                if "color" in all_params:
                    api_params["color"] = all_params["color"]
                    
            elif command == "look_for_object":
                api_params["object_name"] = all_params["object_name"]
                
            elif command == "detect_object":
                api_params["object_type"] = all_params["object_type"]
                if "detection_area" in all_params:
                    api_params["detection_area"] = all_params["detection_area"]
                    
            elif command == "robot_perceive":
                if "perception_area" in all_params:
                    api_params["perception_area"] = all_params["perception_area"]
                    
            # Make API call
            api_url = f"{pycram_api_host}/execute"
            response = requests.post(
                api_url,
                json={"command": command, "params": api_params},
                timeout=requests_timeout,
            )
            
            # Process response
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
                "IMPORTANT: Always specify parameters explicitly by name in the function call."
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

        # add a line/marjer to show begining onew printput
        print("")
        print("=====================================")
        print("Processing new input message...")

        # print the text captured in the input
        print(f"Received message: {message_text}")
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
