# RoboCram API Update Guide

This document serves as a quick reference guide for updating the RoboCram API system when adding, modifying, or removing API endpoints. Follow these steps to ensure all components are properly updated.

## 1. Command Handler Implementation

**File:** `src/robot_api/command_handlers.py`

- Create a new handler class that inherits from `RobotCommandHandler`
- Implement required methods:
  - `__init__`: Define required parameters
  - `validate_params`: Validate parameter types and formats
  - `execute`: Transform params into the API call format
- Add the new handler to `handler_mapping` dictionary at the bottom of the file

```python
class NewCommandHandler(RobotCommandHandler):
    def __init__(self):
        super().__init__(required_params=["param1", "param2"])
        
    def validate_params(self, params: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        valid, error_msg = super().validate_params(params)
        if not valid:
            return False, error_msg
            
        # Add custom validation logic
        
        return True, None
        
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        api_params = {
            "param1": params["param1"],
            "param2": params["param2"],
        }
        
        # Add optional params
        if "optional_param" in params:
            api_params["optional_param"] = params["optional_param"]
            
        return {"command": "new_command", "params": api_params}

# Update the handler_mapping dictionary
handler_mapping = {
    # Existing entries...
    "new_command": NewCommandHandler(),
}
```

## 2. Command Descriptions

**File:** `src/robot_api/command_descriptions.json`

- Add a description for the new command

```json
{
    "existing_command": "Existing description",
    "new_command": "Description of what the new command does and when to use it"
}
```

## 3. Tool Function Parameters

**File:** `src/robot_api/factory.py`

- Update the `robot_api_tool` function signature in the `create_robot_api_tool` function:
  - Add new explicit parameters for the command
  - Add new parameter to the list of parameters in the locals extraction loop

```python
def robot_api_tool(
    command: str = None,
    # Existing params...
    new_param1: type = None,
    new_param2: type = None,
    **kwargs,
):
    # ...existing code...
    
    # Make sure to add your new parameters to this list
    locals_dict = locals()
    for param in [
        "coordinates",
        # ...existing params...
        "new_param1",
        "new_param2",
    ]:
        if param in locals_dict and locals_dict[param] is not None:
            params[param] = locals_dict[param]
```

## 4. Tool Documentation

**File:** `src/robot_api/robochat_tool_api.txt`

- Add the new command with its parameters to the tool documentation

```
- new_command: Brief description of what the command does.
  - Parameters: param1 (type), param2 (type), optional_param (type, optional)
```

## 5. API Documentation

**File:** `robocram_api.md`

- Add a detailed documentation section for the new API endpoint:
  - Parameters table with types, requirements, defaults, and descriptions
  - Return value section with success and error response examples
  - Error conditions
  - Implementation notes

## 6. Testing Implementation (Optional)

**File:** `tests/test_api.py` or equivalent

- Add a test function for the new command to verify it works correctly

## Validation Checklist

Before considering the update complete, verify:

1. ✅ Handler class implements all required methods
2. ✅ Handler added to the handler_mapping dictionary
3. ✅ Command description added to the JSON file
4. ✅ Parameters added to the tool function signature
5. ✅ Parameters added to the locals extraction loop
6. ✅ Documentation updated in the tool API text
7. ✅ Full API documentation created
8. ✅ Test function created (if applicable)

This process ensures that all components of the RoboCram system are properly updated and in sync when modifying the API functionality.