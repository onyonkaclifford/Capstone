from circle_operations import (
    calculate_circle_area,
    calculate_circumference,
    calculate_diameter,
    calculate_radius,
)


def process_user_request(request: str, **kwargs):
    """
    Determines the appropriate circle operation based on user input.

    Args:
        request (str): The user's request or operation name (e.g., "area", "calculate area").
        **kwargs: Additional parameters needed for calculations (radius, diameter, area, circumference).

    Returns:
        str: The result of the selected circle operation.
    """
    request = request.lower().strip()

    # Handle both cases: when operation is passed directly ("area") or in a sentence ("calculate area")
    if "area" in request:
        return calculate_circle_area(**kwargs)
    elif "circumference" in request:
        return calculate_circumference(**kwargs)
    elif "radius" in request:
        return calculate_radius(**kwargs)
    elif "diameter" in request:
        return calculate_diameter(**kwargs)
    else:
        return "Invalid operation. Please specify 'area', 'circumference', 'radius', or 'diameter'."


if __name__ == "__main__":
    # This block only runs when the file is executed directly, not when imported
    while True:
        user_request = input("Enter your request (or type 'exit' to quit): ")
        if user_request.lower() == "exit":
            break

        radius = input("Enter radius (or leave blank): ")
        diameter = input("Enter diameter (or leave blank): ")
        area = input("Enter area (or leave blank): ")
        circumference = input("Enter circumference (or leave blank): ")

        # Convert inputs to float where applicable
        kwargs = {}
        if radius:
            kwargs["radius"] = float(radius)
        if diameter:
            kwargs["diameter"] = float(diameter)
        if area:
            kwargs["area"] = float(area)
        if circumference:
            kwargs["circumference"] = float(circumference)

        result = process_user_request(user_request, **kwargs)
        print(result)
