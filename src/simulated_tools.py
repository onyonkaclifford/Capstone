# simulated_tools.py


def move_robot_simulated(params):
    """
    Simulates moving the robot to a new position.

    Args:
        params (dict): A dictionary containing the 'position' key with the target coordinates.

    Returns:
        str: A message indicating the robot has moved to the specified position.
    """
    print("move robot function is executing....")
    if "position" not in params:
        return "Error: 'position' parameter is missing."

    position = params["position"]
    if not isinstance(position, (list, tuple)) or len(position) != 3:
        return (
            "Error: 'position' must be a list or tuple of three coordinates (x, y, z)."
        )

    return f"Robot moved to {position}."


def spawn_objects_simulated(params):
    """
    Simulates spawning an object with a given name, color, and coordinates.

    Args:
        params (dict): A dictionary containing 'name', 'color', and 'position' keys.

    Returns:
        str: A message indicating the object has been spawned.
    """
    print("spawn robot function is executing....")
    required_keys = ["name", "color", "position"]
    for key in required_keys:
        if key not in params:
            return f"Error: '{key}' parameter is missing."

    name = params["name"]
    color = params["color"]
    position = params["position"]

    if not isinstance(position, (list, tuple)) or len(position) != 3:
        return (
            "Error: 'position' must be a list or tuple of three coordinates (x, y, z)."
        )

    return f"Object '{name}' with color '{color}' spawned at {position}."


def pick_and_place_simulated(params):
    """
    Simulates picking up an object and placing it at a new position.

    Args:
        params (dict): A dictionary containing 'name' and 'position' keys.

    Returns:
        str: A message indicating the object has been picked and placed.
    """
    print("pick and place robot function is executing....")
    required_keys = ["name", "position"]
    for key in required_keys:
        if key not in params:
            return f"Error: '{key}' parameter is missing."

    name = params["name"]
    position = params["position"]

    if not isinstance(position, (list, tuple)) or len(position) != 3:
        return (
            "Error: 'position' must be a list or tuple of three coordinates (x, y, z)."
        )

    return f"Object '{name}' picked and placed at {position}."
