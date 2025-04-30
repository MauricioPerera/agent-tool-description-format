import json
import os
from thefuzz import fuzz

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

def select_tool_by_goal(tools, goal, threshold=75):
    """Select a tool from a list based on fuzzy matching the goal against description or when_to_use."""
    best_match = None
    highest_score = -1

    goal_lower = goal.lower()

    for tool in tools:
        desc_score = fuzz.partial_ratio(goal_lower, tool['description'].lower())
        when_score = fuzz.partial_ratio(goal_lower, tool.get('when_to_use', '').lower())

        current_max_score = max(desc_score, when_score)

        if current_max_score > highest_score and current_max_score >= threshold:
            highest_score = current_max_score
            best_match = tool
            
    if best_match:
        print(f"\nℹ️ Mejor coincidencia encontrada con puntuación: {highest_score} (Umbral: {threshold})")
        
    return best_match
