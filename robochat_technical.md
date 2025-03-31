# RoboCram Technical Documentation

## Architecture Overview

This document provides a comprehensive technical overview of the RoboCram agent's integration with robot control functionality, focusing on the `robot_api_tool` implementation.

```
┌─────────────────┐    ┌──────────────────┐    ┌───────────────────┐
│                 │    │                  │    │                   │
│  Agent (LLM)    │───▶│  robot_api_tool  │───▶│  PyCRAM API       │
│                 │    │                  │    │  (Robot Simulator) │
└─────────────────┘    └──────────────────┘    └───────────────────┘
       │                                                │
       │                                                │
       ▼                                                ▼
┌─────────────────┐                             ┌───────────────────┐
│                 │                             │                   │
│  User Interface │◀────────────────────────────│  Robot Execution  │
│                 │                             │                   │
└─────────────────┘                             └───────────────────┘
```

## Robot API Tool Implementation

### Function Signature

The `robot_api_tool` function is designed with explicit parameter typing to handle various robot commands:

```python
def robot_api_tool(command: str = None, coordinates: list = None, object_name: str = None, 
                  target_location: list = None, arm: str = None, object_choice: str = None,
                  color: str = None, perception_area: str = None, object_type: str = None,
                  detection_area: str = None, **kwargs):
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
```

### Parameter Handling

The function combines explicit parameters with generic `**kwargs` for maximum flexibility:

1. **Explicit Parameters**: All common parameters are explicitly defined, allowing for type checking and IDE assistance.
2. **kwargs Aggregation**: All explicit parameters are merged into kwargs for unified processing:

```python
# Convert explicitly provided parameters to kwargs for uniform handling
if coordinates is not None:
    kwargs['coordinates'] = coordinates
if object_name is not None:
    kwargs['object_name'] = object_name
# ... additional parameters ...
```

### Validation and Error Handling

The implementation includes comprehensive validation to catch common errors before making API requests:

1. **Command-specific Validation**:
   ```python
   if command == 'move_robot' and 'coordinates' not in kwargs:
       return "ERROR: move_robot command requires 'coordinates' parameter. Make sure to pass it as coordinates=[x, y, z]"
   ```

2. **Missing Parameter Detection**:
   ```python
   if command in ['pickup_and_place', 'transport_object']:
       missing_params = []
       if 'object_name' not in kwargs: missing_params.append('object_name')
       if 'target_location' not in kwargs: missing_params.append('target_location')
       if missing_params:
           return f"ERROR: {command} command requires these missing parameters: {', '.join(missing_params)}. Make sure to pass them explicitly by name."
   ```

3. **Parameter Type Validation**:
   ```python
   coords = kwargs['coordinates']
   if isinstance(coords, list) and len(coords) == 3:
       params['coordinates'] = [float(coords[0]), float(coords[1]), float(coords[2])]
   else:
       return "Error: coordinates must be a list of exactly 3 values [x, y, z]"
   ```

### API Communication

The tool communicates with the robot simulator via HTTP requests:

```python
# API endpoint 
api_url = "http://192.168.1.64:8001/execute"

# Prepare request payload
payload = {
    "command": command,
    "params": params
}

# Make the API request
response = requests.post(api_url, json=payload)
```

## Structured Tool Integration

The `robot_api_tool` is integrated into the LangChain framework using a `StructuredTool`:

```python
robot_tool_structured = StructuredTool.from_function(
    func=robot_api_tool,
    name="RobotControl",
    description=(
        "Use this tool to control the robot simulator. Each command requires specific parameters:\n"
        "- move_robot: coordinates=[x, y, z]\n"
        "- pickup_and_place: object_name, target_location=[x, y, z], arm (optional: 'left' or 'right')\n"
        # ... additional command descriptions ...
        "IMPORTANT: Always specify parameters explicitly by name in the function call. For example, use:\n"
        "command='move_robot', coordinates=[x, y, z]\n"
        "and NOT just command='move_robot' with coordinates in a separate parameter."
    ),
)
```

This integration enables the LLM to understand:
1. When to use the robot tool
2. What parameters are required for each command
3. How to properly format those parameters

## System Message Configuration

The agent's system message provides explicit guidance on robot command usage:

```python
system_message = SystemMessage(
    content=(
        # ... general instructions ...
        
        "\n\n2. ROBOT CONTROL: Map natural language requests to specific robot commands:"
        "\n- For movement requests: Use command='move_robot' with coordinates=[x, y, z]"
        "\n- For object manipulation: Use command='pickup_and_place' with object_name, target_location=[x, y, z], and arm"
        # ... additional command mappings ...
        
        "\n\nIMPORTANT: Always pass parameters with explicit names. For example:"
        "\n- CORRECT: command='move_robot', coordinates=[2, 3, 0]"
        "\n- INCORRECT: command='move_robot', [2, 3, 0]"
        
        "\n\nCOMMAND MAPPING EXAMPLES:"
        "\n- 'Move the robot to position 2, 3, 0' → command='move_robot', coordinates=[2, 3, 0]"
        # ... additional examples ...
    )
)
```

## Supported Robot Commands

| Command | Required Parameters | Optional Parameters | Description |
|---------|---------------------|---------------------|-------------|
| `move_robot` | coordinates=[x, y, z] | None | Moves the robot to specified coordinates |
| `pickup_and_place` | object_name, target_location=[x, y, z] | arm | Picks up an object and places it at target location |
| `spawn_objects` | object_choice, coordinates=[x, y, z] | color | Creates a new object at specified coordinates |
| `robot_perceive` | None | perception_area | Scans the environment or specific area |
| `look_for_object` | object_name | None | Searches for a specific object |
| `unpack_arms` | None | None | Prepares robot arms for use |
| `detect_object` | object_type | detection_area | Detects objects of a specific type |
| `transport_object` | object_name, target_location=[x, y, z] | arm | Moves an object to target location |

## Parameter Value Constraints

- **coordinates/target_location**: Must be a list of exactly 3 float values [x, y, z]
- **arm**: Must be either 'left', 'right', or None (for automatic selection)
- **object_choice**: Limited to 'cereal', 'milk', 'spoon', 'bowl'
- **color**: Available options are 'red', 'blue', 'green', 'yellow', 'white', 'black'

## Common Integration Issues and Solutions

### Issue: Empty kwargs Dictionary

**Problem**: When parameters are passed positionally instead of by name, they don't reach the function correctly.

**Solution**: 
1. Explicit parameter declaration in function signature
2. Clear documentation in the tool description
3. Validation checks that provide helpful error messages
4. System message examples showing correct parameter usage

### Issue: Parameter Type Validation Errors

**Problem**: Parameters received with incorrect types or formats.

**Solution**:
1. Type hints in function signature
2. Explicit type checking in function body
3. Conversion of coordinate values to float
4. Clear error messages explaining expected formats

### Issue: API Communication Failures

**Problem**: Connection issues with the robot simulator API.

**Solution**:
1. Try-except blocks around API calls
2. Clear error reporting
3. Configurable API endpoint URL

## Debugging and Monitoring

The integration includes debugging output to monitor function calls:

```python
# Print debug information
print(f"Command: {command}")
print(f"Kwargs: {kwargs}")
```

This allows for tracking:
1. What commands are being issued
2. What parameters are being received
3. If parameters are being passed correctly

## Best Practices for Extending the Tool

When adding new robot commands or modifying existing ones:

1. **Update function signature**: Add explicit parameters for clarity
2. **Update parameter extraction code**: Ensure new parameters are correctly handled
3. **Add validation logic**: Validate parameters before sending to API
4. **Update documentation**: Modify tool description and system message
5. **Test interaction**: Verify the LLM correctly uses the new parameters

## Technical Implementation of Command Handling

Each command requires specific parameter handling. For example, here's how `move_robot` is implemented:

```python
if command == 'move_robot':
    # Handle move_robot command (requires coordinates)
    if 'coordinates' not in kwargs:
        return "Error: 'move_robot' command requires 'coordinates' parameter"
    
    coords = kwargs['coordinates']
    if isinstance(coords, list) and len(coords) == 3:
        params['coordinates'] = [float(coords[0]), float(coords[1]), float(coords[2])]
    else:
        return "Error: coordinates must be a list of exactly 3 values [x, y, z]"
```

## API Request Format

The tool sends a JSON payload to the robot simulator API:

```json
{
  "command": "move_robot",
  "params": {
    "coordinates": [2.0, 3.0, 0.0]
  }
}
```

## API Response Handling

The tool processes API responses and formats them for the user:

```python
if response.status_code == 200:
    result = response.json()
    return json.dumps(result, indent=2)  # Return formatted JSON response
else:
    return f"API error: {response.status_code} - {response.text}"
```

---

## Advanced Implementation Notes

### Function Component Breakdown

1. **Parameter Validation**: First phase validates presence and format of required parameters
2. **Command-Specific Logic**: Each command has a dedicated processing section
3. **Parameter Processing**: Converts and formats parameters for the API
4. **API Request Construction**: Builds appropriate request payload
5. **API Communication**: Handles HTTP request/response cycle
6. **Error Handling**: Catches and formats API errors

### Agent Integration Points

1. **Tool Registration**: Added to the agent's tools list
2. **System Message**: Provides guidance on when and how to use the tool
3. **LLM Interaction**: LLM selects when to use the tool based on user input
4. **Response Processing**: Tool responses are incorporated into the agent's overall response

### Command-Intent Mapping

The system message provides specific natural language patterns that should trigger tool usage:

- "Any request mentioning 'pick', 'grab', 'take', or 'get' + placing = 'pickup_and_place'"
- "Any request mentioning 'move' or 'go' + robot = 'move_robot'"
- "Any request mentioning 'move' + object name = 'transport_object'"

This helps the LLM correctly map user intents to specific robot commands. 