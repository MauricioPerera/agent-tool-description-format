import json
import os

def load_tool(filepath):
    """Load a single ATDF tool description from a JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Tool file '{filepath}' not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{filepath}': {e}")
        return None

def load_tools_from_directory(directory):
    """Load all ATDF tool descriptions from a directory."""
    tools = []
    if not os.path.exists(directory):
        print(f"Error: Directory '{directory}' does not exist.")
        return tools

    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            filepath = os.path.join(directory, filename)
            tool = load_tool(filepath)
            if tool:
                tools.append(tool)
    return tools

def select_tool_by_goal(tools, goal):
    """Select a tool from a list based on a goal (matches description or when_to_use)."""
    for tool in tools:
        if (goal.lower() in tool['description'].lower() or 
            goal.lower() in tool['when_to_use'].lower()):
            return tool
    return None
