import os
import socket

from circle_operations import (
    calculate_circle_area,
    calculate_circumference,
    calculate_diameter,
    calculate_radius,
)
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

# Print debug info about network interfaces
hostname = socket.gethostname()
print(f"Host name: {hostname}")
try:
    host_ip = socket.gethostbyname(hostname)
    print(f"Host IP: {host_ip}")
except:
    print("Unable to get Host IP")

print("All available IP addresses:")
try:
    for ip in socket.gethostbyname_ex(socket.gethostname())[2]:
        print(f"- {ip}")
except:
    print("Unable to list all IPs")

app = FastAPI()

# Create static directory if it doesn't exist
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=static_dir), name="static")


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


@app.get("/", response_class=HTMLResponse)
async def get_html():
    """Serve the main HTML page."""
    html_path = os.path.join(os.path.dirname(__file__), "circle.html")
    try:
        with open(html_path, "r") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        print(f"Error reading HTML file: {e}")
        return HTMLResponse(
            content=f"""
        <html>
            <head>
                <title>Circle Calculator</title>
            </head>
            <body>
                <h1>Circle Calculator</h1>
                <p>Error loading the main interface: {str(e)}</p>
                <p>Path attempted: {html_path}</p>
            </body>
        </html>
        """
        )


@app.get("/circle")
def circle_operation(
    operation: str = Query(
        ...,
        description="Specify the operation: area, circumference, radius, or diameter",
    ),
    radius: float = Query(None, description="Radius of the circle"),
    diameter: float = Query(None, description="Diameter of the circle"),
    area: float = Query(None, description="Area of the circle"),
    circumference: float = Query(None, description="Circumference of the circle"),
):
    """API endpoint to perform circle operations based on user query."""
    print(
        f"API call received: operation={operation}, radius={radius}, diameter={diameter}, area={area}, circumference={circumference}"
    )

    kwargs = {
        "radius": radius,
        "diameter": diameter,
        "area": area,
        "circumference": circumference,
    }
    kwargs = {k: v for k, v in kwargs.items() if v is not None}  # Remove None values

    print(f"Processing with parameters: {kwargs}")
    result = process_user_request(operation, **kwargs)
    print(f"Result: {result}")

    return {"result": result}


if __name__ == "__main__":
    import uvicorn

    port = 8002
    print(f"Starting server on all interfaces (0.0.0.0) on port {port}")
    print(f"Try accessing the application at:")
    print(f"- http://localhost:{port}")
    print(f"- http://127.0.0.1:{port}")
    print(f"- http://192.168.1.82:{port} (from other devices on your network)")
    uvicorn.run(app, host="0.0.0.0", port=port)
