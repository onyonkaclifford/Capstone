import math


def calculate_circle_area(radius: float = None, diameter: float = None):
    """Calculate the area of a circle given either the radius or diameter."""
    if radius is None and diameter is None:
        return "Please provide either the radius or diameter to calculate the area."

    if diameter is not None:
        radius = diameter / 2  # Convert diameter to radius

    area = math.pi * (radius**2)
    return f"The area of a circle with radius {radius:.2f} is {area:.2f} square units."


def calculate_circumference(radius: float = None, diameter: float = None):
    """Calculate the circumference given the radius or diameter."""
    if radius is None and diameter is None:
        return "Please provide either the radius or diameter to calculate the circumference."

    if diameter is not None:
        radius = diameter / 2

    circumference = 2 * math.pi * radius
    return f"The circumference of a circle with radius {radius:.2f} is {circumference:.2f} units."


def calculate_radius(area: float = None, circumference: float = None):
    """Calculate the radius given area or circumference."""
    if area is None and circumference is None:
        return (
            "Please provide either the area or circumference to calculate the radius."
        )

    if area is not None:
        radius = math.sqrt(area / math.pi)
        return f"The radius of a circle with area {area:.2f} is {radius:.2f} units."

    # No need for if check since we know circumference must be not None at this point
    radius = circumference / (2 * math.pi)
    return f"The radius of a circle with circumference {circumference:.2f} is {radius:.2f} units."


def calculate_diameter(area: float = None, circumference: float = None):
    """Calculate the diameter given area or circumference."""
    if area is None and circumference is None:
        return (
            "Please provide either the area or circumference to calculate the diameter."
        )

    radius_result = calculate_radius(area=area, circumference=circumference)

    if "radius" in radius_result:
        radius_value = float(radius_result.split()[-2])  # Extract numeric value
        diameter = 2 * radius_value
        return f"The diameter of a circle is {diameter:.2f} units."

    return radius_result  # Error message if applicable
