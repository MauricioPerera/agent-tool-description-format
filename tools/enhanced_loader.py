import json
import os
import re
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("enhanced_loader")


def load_tool(filepath):
    """Load a single ATDF tool description from a JSON file with enhanced features support."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            tool = json.load(f)
            # Add the filepath to metadata
            if "metadata" not in tool:
                tool["metadata"] = {}
            tool["metadata"]["_filepath"] = filepath
            return tool
    except FileNotFoundError:
        logger.error(f"Error: Tool file '{filepath}' not found.")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Error: Invalid JSON in '{filepath}': {e}")
        return None


def load_tools_from_directory(directory):
    """Load all ATDF tool descriptions from a directory, supporting enhanced features."""
    tools = []
    if not os.path.exists(directory):
        logger.error(f"Error: Directory '{directory}' does not exist.")
        return tools

    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            filepath = os.path.join(directory, filename)
            tool = load_tool(filepath)
            if tool:
                # Add the filename to the tool metadata
                if "metadata" not in tool:
                    tool["metadata"] = {}
                tool["metadata"]["_filename"] = filename

                # Determine language from filename or localization field
                if "_es." in filename:
                    tool["metadata"]["_language"] = "es"
                elif "_en." in filename:
                    tool["metadata"]["_language"] = "en"
                elif "_pt." in filename:
                    tool["metadata"]["_language"] = "pt"
                elif "localization" in tool:
                    # If localization exists, use the first language as default
                    if tool["localization"]:
                        tool["metadata"]["_language"] = next(
                            iter(tool["localization"].keys())
                        )
                else:
                    # Default language detection based on description
                    tool["metadata"]["_language"] = detect_language(tool["description"])

                tools.append(tool)
    return tools


def detect_language(text):
    """Enhanced language detection based on common words and patterns."""
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
        "superficie",
        "herramienta",
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
        "surface",
        "tool",
    ]
    pt_markers = [
        "criar",
        "fazer",
        "usar",
        "quando",
        "precisar",
        "furo",
        "traduzir",
        "texto",
        "permite",
        "superfície",
        "ferramenta",
    ]

    # Count occurrences of marker words
    es_count = sum(1 for word in es_markers if word in text.lower())
    en_count = sum(1 for word in en_markers if word in text.lower())
    pt_count = sum(1 for word in pt_markers if word in text.lower())

    # Additional pattern matching for common language structures
    if re.search(r"\b(el|la|los|las|que|para|cuando)\b", text.lower()):
        es_count += 2
    if re.search(r"\b(the|is|are|to|when|this|that)\b", text.lower()):
        en_count += 2
    if re.search(r"\b(o|a|os|as|que|para|quando)\b", text.lower()):
        pt_count += 2

    # Determine the most likely language
    if pt_count > es_count and pt_count > en_count:
        return "pt"
    elif es_count > en_count:
        return "es"
    else:
        return "en"


def select_tool_by_goal(tools, goal, user_language=None):
    """Select a tool from a list based on a goal with enhanced language awareness."""
    # Detect the language of the query if not specified
    query_language = user_language or detect_language(goal)
    logger.info(f"Query language detected as: {query_language}")

    # Prepare list of relevant tools based on language
    language_preferred_tools = []
    other_tools = []

    for tool in tools:
        tool_language = tool.get("metadata", {}).get("_language", "en")

        # Check if the tool has localization for the query language
        has_query_language = False
        if "localization" in tool and query_language in tool["localization"]:
            has_query_language = True

        if tool_language == query_language or has_query_language:
            language_preferred_tools.append(tool)
        else:
            other_tools.append(tool)

    # Search functions
    def exact_match(tool):
        """Check if goal is an exact substring of description or when_to_use."""
        # Use localized fields if available for the query language
        if "localization" in tool and query_language in tool["localization"]:
            desc = tool["localization"][query_language]["description"].lower()
            when = tool["localization"][query_language]["when_to_use"].lower()
        else:
            desc = tool["description"].lower()
            when = tool["when_to_use"].lower()

        return goal.lower() in desc or goal.lower() in when

    def keyword_match(tool, keywords):
        """Check if any keyword is found in description or when_to_use."""
        # Use localized fields if available for the query language
        if "localization" in tool and query_language in tool["localization"]:
            desc = tool["localization"][query_language]["description"].lower()
            when = tool["localization"][query_language]["when_to_use"].lower()
        else:
            desc = tool["description"].lower()
            when = tool["when_to_use"].lower()

        # Also check tags if available
        tags = []
        if "metadata" in tool and "tags" in tool["metadata"]:
            tags = [tag.lower() for tag in tool["metadata"]["tags"]]

        for keyword in keywords:
            if (
                keyword in desc
                or keyword in when
                or keyword in tags
                or any(
                    keyword in example.get("title", "").lower()
                    for example in tool.get("examples", [])
                )
            ):
                return True
        return False

    # 1. First, try exact substring match in language-preferred tools
    for tool in language_preferred_tools:
        if exact_match(tool):
            logger.info(f"Found exact match in preferred language: {tool['tool_id']}")
            return tool

    # 2. Extract keywords from the goal
    keywords = extract_keywords(goal, query_language)
    logger.info(f"Extracted keywords: {keywords}")

    # 3. Try keyword match in language-preferred tools
    for tool in language_preferred_tools:
        if keyword_match(tool, keywords):
            logger.info(f"Found keyword match in preferred language: {tool['tool_id']}")
            return tool

    # 4. If no match in language-preferred tools, try exact match in all tools
    for tool in other_tools:
        if exact_match(tool):
            logger.info(
                f"Found exact match in non-preferred language: {tool['tool_id']}"
            )
            return tool

    # 5. Try keyword match in all tools
    for tool in other_tools:
        if keyword_match(tool, keywords):
            logger.info(
                f"Found keyword match in non-preferred language: {tool['tool_id']}"
            )
            return tool

    # 6. If no match, look at examples if available
    for tool in tools:
        for example in tool.get("examples", []):
            example_title = example.get("title", "").lower()
            example_desc = example.get("description", "").lower()
            if (
                goal.lower() in example_title
                or goal.lower() in example_desc
                or any(kw in example_title or kw in example_desc for kw in keywords)
            ):
                logger.info(f"Found match in examples: {tool['tool_id']}")
                return tool

    # No match found
    logger.warning(f"No suitable tool found for goal: {goal}")
    return None


def extract_keywords(text, language="en"):
    """Extract significant keywords from a text based on language."""
    # Common stopwords by language
    stopwords = {
        "en": [
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "if",
            "because",
            "as",
            "what",
            "when",
            "where",
            "how",
            "why",
            "which",
            "who",
            "whom",
            "this",
            "that",
            "these",
            "those",
            "am",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "can",
            "could",
            "should",
            "would",
            "i",
            "you",
            "he",
            "she",
            "we",
            "they",
            "need",
            "want",
            "use",
        ],
        "es": [
            "el",
            "la",
            "los",
            "las",
            "un",
            "una",
            "unos",
            "unas",
            "y",
            "o",
            "pero",
            "si",
            "porque",
            "como",
            "qué",
            "cuando",
            "donde",
            "cómo",
            "por qué",
            "quién",
            "quienes",
            "este",
            "esta",
            "estos",
            "estas",
            "ese",
            "esa",
            "esos",
            "esas",
            "soy",
            "eres",
            "es",
            "somos",
            "son",
            "era",
            "eras",
            "éramos",
            "eran",
            "ser",
            "sido",
            "estar",
            "he",
            "has",
            "ha",
            "hemos",
            "han",
            "hago",
            "haces",
            "hace",
            "hacemos",
            "hacen",
            "puedo",
            "puedes",
            "puede",
            "podemos",
            "pueden",
            "yo",
            "tú",
            "él",
            "ella",
            "nosotros",
            "ellos",
            "ellas",
            "necesito",
            "quiero",
            "usar",
        ],
        "pt": [
            "o",
            "a",
            "os",
            "as",
            "um",
            "uma",
            "uns",
            "umas",
            "e",
            "ou",
            "mas",
            "se",
            "porque",
            "como",
            "que",
            "quando",
            "onde",
            "como",
            "por que",
            "quem",
            "quais",
            "este",
            "esta",
            "estes",
            "estas",
            "esse",
            "essa",
            "esses",
            "essas",
            "sou",
            "és",
            "é",
            "somos",
            "são",
            "era",
            "eras",
            "éramos",
            "eram",
            "ser",
            "sido",
            "estar",
            "tenho",
            "tens",
            "tem",
            "temos",
            "têm",
            "faço",
            "fazes",
            "faz",
            "fazemos",
            "fazem",
            "posso",
            "podes",
            "pode",
            "podemos",
            "podem",
            "eu",
            "tu",
            "ele",
            "ela",
            "nós",
            "eles",
            "elas",
            "preciso",
            "quero",
            "usar",
        ],
    }

    # Get appropriate stopword list
    stop_list = stopwords.get(language, stopwords["en"])

    # Tokenize text to words
    words = re.findall(r"\w+", text.lower())

    # Filter out stopwords and short words
    keywords = [word for word in words if word not in stop_list and len(word) > 2]

    # Add any multi-word phrases that might be important (like "make a hole")
    important_phrases = {
        "en": ["make a hole", "create a hole", "translate text", "paint a picture"],
        "es": [
            "hacer un agujero",
            "crear un agujero",
            "traducir texto",
            "pintar un cuadro",
        ],
        "pt": ["fazer um furo", "criar um furo", "traduzir texto", "pintar um quadro"],
    }

    phrases_list = important_phrases.get(language, [])
    for phrase in phrases_list:
        if phrase in text.lower():
            keywords.append(phrase)

    return keywords


def get_tool_examples(tool, num_examples=2, language=None):
    """Get a selection of examples from a tool description.

    Args:
        tool: The tool description dictionary
        num_examples: Maximum number of examples to return
        language: Preferred language for example selection

    Returns:
        List of example dictionaries
    """
    if "examples" not in tool or not tool["examples"]:
        return []

    # If language is specified, try to find examples that match the language
    if language and "localization" in tool and language in tool["localization"]:
        # If there are language-specific examples, prioritize those
        language_examples = [
            ex for ex in tool["examples"] if ex.get("language") == language
        ]
        if language_examples:
            return language_examples[:num_examples]

    # Otherwise return the first n examples
    return tool["examples"][:num_examples]


def get_tool_prerequisites(tool):
    """Get the prerequisites for using a tool, if specified."""
    if "prerequisites" not in tool:
        return None
    return tool["prerequisites"]


def get_localized_description(tool, language):
    """Get tool description in the specified language if available."""
    if "localization" in tool and language in tool["localization"]:
        return tool["localization"][language]["description"]
    return tool["description"]


def get_localized_when_to_use(tool, language):
    """Get tool usage context in the specified language if available."""
    if "localization" in tool and language in tool["localization"]:
        return tool["localization"][language]["when_to_use"]
    return tool["when_to_use"]
