# RoboCram User Guide

## Introduction

Welcome to RoboCram, your advanced AI assistant for robot control and calculations! RoboCram helps you interact with robots using natural language commands, making robot control accessible and intuitive. This guide will help you understand what RoboCram can do and how to effectively communicate with it.

## What Can RoboCram Do?

RoboCram can help you with:

1. **Robot Movement and Manipulation**: Move the robot, pick up objects, and place them at specific locations
2. **Object Creation**: Spawn various objects in the simulator
3. **Perception**: Scan the environment and detect objects
4. **Circle Calculations**: Perform area, circumference, radius, and diameter calculations

## Robot Commands Guide

### Moving the Robot

To move the robot to specific coordinates:

```
Move the robot to position 2, 3, 0
Go to coordinates 1.5, 2.1, 0
Navigate to 3, 4, 0
```

### Manipulating Objects

To pick up objects and place them elsewhere:

```
Pick up the milk and place it at 1, 2, 0.8
Grab the cereal box and move it to 2, 3, 1
Take the spoon and put it at 1.5, 1.2, 0.9
```

You can specify which arm to use:

```
Use the left arm to pick up the bowl and place it at 2, 1, 0.8
With your right arm, move the milk to 1.5, 2, 0.9
```

### Creating Objects

To spawn new objects in the simulation:

```
Create a bowl at position 1.4, 1, 0.95
Spawn a cereal box at 2, 3, 1
Add a red spoon at 1.5, 1.2, 0.9
Place a blue milk carton at 1, 2, 0.8
```

Available objects:
- Cereal box
- Milk carton
- Spoon
- Bowl

Available colors:
- Red
- Blue
- Green
- Yellow
- White
- Black

### Perception & Detection

To see what's in the environment:

```
What objects are on the table?
Scan the kitchen area
Look around and tell me what you see
```

To find specific objects:

```
Find the cereal box
Where is the milk?
Locate the spoon
```

To detect objects of a certain type:

```
Detect all bowls
Find any spoons in the area
Identify cereal boxes in the kitchen
```

### Unpacking Arms

To prepare the robot for manipulation:

```
Unpack your arms
Get your arms ready
```

## Example Scenarios

### Making Breakfast

```
1. Unpack your arms
2. Move the robot to position 2, 3, 0
3. Spawn a bowl at 1.5, 2, 0.9
4. Create a cereal box at 2, 2, 0.9
5. Add a milk carton at 2.5, 2, 0.9
6. Pick up the cereal box and place it near the bowl at 1.7, 2, 0.9
7. With your right arm, move the milk to 1.3, 2, 0.9
```

### Organizing Objects

```
1. Scan the table to see what objects are present
2. Find the milk
3. Pick up the milk and place it at 1, 2, 0.8
4. Look for the cereal box
5. Move the cereal box to 2, 2, 0.9
```

## Troubleshooting

### Common Issues

1. **Coordinates Format**: Always use three numbers for coordinates [x, y, z]
2. **Object Names**: Use specific object names: milk, cereal, spoon, bowl
3. **Command Clarity**: Be specific about what you want the robot to do
4. **Parameter Requirements**: Some commands require specific parameters, if missing RoboCram will let you know

### If the Robot Doesn't Respond Correctly

- Try rephrasing your request
- Make sure you're providing all required details (locations, object names)
- Check that the object or position exists in the simulator
- For complex tasks, break them down into individual steps

## Circle Calculations

RoboCram can also perform circle calculations:

```
What is the area of a circle with radius 5?
Calculate the circumference of a circle with diameter 10
If a circle has an area of 25π, what is its radius?
What is the diameter of a circle with circumference 20π?
```

---

## Tips for Effective Communication

1. **Be Specific**: Clearly state the action, object, and location
2. **Use Natural Language**: You don't need special syntax, just speak naturally
3. **Provide All Required Information**: Include coordinates as [x, y, z] and specific object names
4. **One Task at a Time**: For complex operations, issue separate commands for each step
5. **Ask for Help**: If you're unsure about a command, just ask RoboCram for help!

Enjoy using RoboCram for your robot control needs! 