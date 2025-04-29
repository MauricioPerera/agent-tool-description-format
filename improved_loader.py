import json
import os
import re

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
                # Add the filename to the tool metadata
                tool['_filename'] = filename
                # Try to determine language from filename
                if '_es.' in filename:
                    tool['_language'] = 'es'
                elif '_en.' in filename:
                    tool['_language'] = 'en'
                elif '_pt.' in filename:
                    tool['_language'] = 'pt'
                else:
                    # Default language detection based on description
                    tool['_language'] = detect_language(tool['description'])
                tools.append(tool)
    return tools

def detect_language(text):
    """Simple language detection based on common words."""
    es_markers = ['hacer', 'crear', 'usar', 'cuando', 'necesites', 'agujero', 'traducir', 'texto', 'permite']
    en_markers = ['make', 'create', 'use', 'when', 'need', 'hole', 'translate', 'text', 'creates']
    pt_markers = ['criar', 'fazer', 'usar', 'quando', 'precisar', 'furo', 'traduzir', 'texto', 'permite']
    
    es_count = sum(1 for word in es_markers if word in text.lower())
    en_count = sum(1 for word in en_markers if word in text.lower())
    pt_count = sum(1 for word in pt_markers if word in text.lower())
    
    if pt_count > es_count and pt_count > en_count:
        return 'pt'
    elif es_count > en_count:
        return 'es'
    else:
        return 'en'

def select_tool_by_goal(tools, goal):
    """Select a tool from a list based on a goal with language awareness."""
    # Detect the language of the query
    query_language = detect_language(goal)
    
    # First, look for exact matches in tools with matching language
    language_tools = [tool for tool in tools if tool.get('_language') == query_language]
    
    # 1. Try exact substring match in language-preferred tools
    for tool in language_tools:
        if (goal.lower() in tool['description'].lower() or 
            goal.lower() in tool['when_to_use'].lower()):
            return tool
    
    # 2. Try keyword match in language-preferred tools
    keyword_map = {
        'es': {
            'hacer un agujero': ['agujero', 'perfor', 'hueco'],
            'traducir texto': ['traduc', 'texto', 'idioma']
        },
        'en': {
            'make a hole': ['hole', 'drill', 'perforat'],
            'translate text': ['translat', 'text', 'language']
        },
        'pt': {
            'fazer um furo': ['furo', 'perfur', 'buraco'],
            'traduzir texto': ['traduz', 'texto', 'idioma']
        }
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
        stopwords = {
            'en': ['when', 'need', 'make', 'the', 'and', 'for'],
            'es': ['usar', 'para', 'cuando', 'necesito', 'quiero', 'como'],
            'pt': ['usar', 'para', 'quando', 'preciso', 'quero', 'como']
        }
        
        ignore_words = stopwords.get(query_language, [])
        search_keywords = [word for word in goal.lower().split() 
                          if len(word) > 3 and word not in ignore_words]
    
    # Try to find a match using keywords in language-preferred tools
    if search_keywords:
        for tool in language_tools:
            description = tool['description'].lower()
            when_to_use = tool['when_to_use'].lower()
            
            if any(keyword in description or keyword in when_to_use for keyword in search_keywords):
                return tool
    
    # 3. If no match in language-preferred tools, fall back to all tools with same preferences
    all_tools = tools
    
    # Try exact substring match in all tools
    for tool in all_tools:
        if (goal.lower() in tool['description'].lower() or 
            goal.lower() in tool['when_to_use'].lower()):
            return tool
    
    # Try keyword match in all tools
    if search_keywords:
        for tool in all_tools:
            description = tool['description'].lower()
            when_to_use = tool['when_to_use'].lower()
            
            if any(keyword in description or keyword in when_to_use for keyword in search_keywords):
                return tool
    
    # No match found
    return None 