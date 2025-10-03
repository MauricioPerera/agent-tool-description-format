import json
import os
import re


def load_tool(filepath):
    """Load a single ATDF tool description from a JSON file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
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
        if filename.endswith(".json"):
            filepath = os.path.join(directory, filename)
            tool = load_tool(filepath)
            if tool:
                # Add the filename to the tool metadata
                tool["_filename"] = filename
                # Try to determine language from filename
                if "_es." in filename:
                    tool["_language"] = "es"
                elif "_en." in filename:
                    tool["_language"] = "en"
                else:
                    # Default language detection based on description
                    tool["_language"] = detect_language(tool["description"])
                tools.append(tool)
    return tools


def detect_language(text):
    """Simple language detection based on common words."""
    es_markers = [
        "hacer",
        "crear",
        "usar",
        "cuando",
        "necesites",
        "agujero",
        "traducir",
        "texto",
        "permite",
    ]
    en_markers = [
        "make",
        "create",
        "use",
        "when",
        "need",
        "hole",
        "translate",
        "text",
        "creates",
    ]

    es_count = sum(1 for word in es_markers if word in text.lower())
    en_count = sum(1 for word in en_markers if word in text.lower())

    return "es" if es_count > en_count else "en"


def select_tool_by_goal(tools, goal):
    """Select a tool from a list based on a goal with language awareness."""
    # Detect the language of the query
    query_language = detect_language(goal)

    # First, look for exact matches in tools with matching language
    language_tools = [tool for tool in tools if tool.get("_language") == query_language]

    # 1. Try exact substring match in language-preferred tools
    for tool in language_tools:
        if (
            goal.lower() in tool["description"].lower()
            or goal.lower() in tool["when_to_use"].lower()
        ):
            return tool

    # 2. Try keyword match in language-preferred tools
    keyword_map = {
        "es": {
            "hacer un agujero": ["agujero", "perfor", "hueco"],
            "traducir texto": ["traduc", "texto", "idioma"],
        },
        "en": {
            "make a hole": ["hole", "drill", "perforat"],
            "translate text": ["translat", "text", "language"],
        },
    }

    # Get relevant keywords based on goal and language
    search_keywords = []
    for query, keywords in keyword_map.get(query_language, {}).items():
        if query in goal.lower():
            search_keywords = keywords
            break

    # If we don't have specific keywords, extract them from the goal
    if not search_keywords and len(goal.split()) > 0:
        # Use the significant words from the goal as keywords
        search_keywords = [
            word
            for word in goal.lower().split()
            if len(word) > 3
            and word not in ["when", "need", "make", "usar", "para", "cuando"]
        ]

    # Try to find a match using keywords in language-preferred tools
    if search_keywords:
        for tool in language_tools:
            description = tool["description"].lower()
            when_to_use = tool["when_to_use"].lower()

            if any(
                keyword in description or keyword in when_to_use
                for keyword in search_keywords
            ):
                return tool

    # 3. If no match in language-preferred tools, fall back to all tools with same preferences
    all_tools = tools

    # Try exact substring match in all tools
    for tool in all_tools:
        if (
            goal.lower() in tool["description"].lower()
            or goal.lower() in tool["when_to_use"].lower()
        ):
            return tool

    # Try keyword match in all tools
    if search_keywords:
        for tool in all_tools:
            description = tool["description"].lower()
            when_to_use = tool["when_to_use"].lower()

            if any(
                keyword in description or keyword in when_to_use
                for keyword in search_keywords
            ):
                return tool

    # No match found
    return None
