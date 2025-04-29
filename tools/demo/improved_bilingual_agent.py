import os
from improved_loader import load_tools_from_directory, select_tool_by_goal, detect_language

def print_tool_info(selected_tool, language="es"):
    """Print tool information in the specified language."""
    if language == "es":
        print(f"\n🎯 Herramienta seleccionada: {selected_tool['tool_id']}\n")
        print(f"➤ ¿Qué hace?: {selected_tool['description']}")
        print(f"➤ ¿Cuándo usarla?: {selected_tool['when_to_use']}")
        print(f"➤ ¿Cómo usarla?:")
        print(f"  - Entradas:")
        for input_param in selected_tool['how_to_use']['inputs']:
            print(f"    * {input_param['name']} ({input_param['type']}): {input_param.get('description', 'Sin descripción')}")
        print(f"  - Salidas:")
        print(f"    * Éxito: {selected_tool['how_to_use']['outputs']['success']}")
        print(f"    * Posibles errores:")
        for error in selected_tool['how_to_use']['outputs']['failure']:
            print(f"      - {error['code']}: {error['description']}")
    else:  # English by default
        print(f"\n🎯 Selected tool: {selected_tool['tool_id']}\n")
        print(f"➤ What it does: {selected_tool['description']}")
        print(f"➤ When to use it: {selected_tool['when_to_use']}")
        print(f"➤ How to use it:")
        print(f"  - Inputs:")
        for input_param in selected_tool['how_to_use']['inputs']:
            print(f"    * {input_param['name']} ({input_param['type']}): {input_param.get('description', 'No description')}")
        print(f"  - Outputs:")
        print(f"    * Success: {selected_tool['how_to_use']['outputs']['success']}")
        print(f"    * Possible errors:")
        for error in selected_tool['how_to_use']['outputs']['failure']:
            print(f"      - {error['code']}: {error['description']}")

def test_goal(tools, goal):
    """Test a goal and display the result."""
    language = detect_language(goal)
    print(f"\n=============== {'ESPAÑOL' if language == 'es' else 'ENGLISH'} ===============")
    print(f"Objetivo/Goal: '{goal}'")
    
    selected_tool = select_tool_by_goal(tools, goal)
    if selected_tool:
        print_tool_info(selected_tool, language)
    else:
        if language == "es":
            print(f"⚠️ No se encontró una herramienta adecuada para el objetivo: '{goal}'.")
        else:
            print(f"⚠️ No suitable tool was found for the goal: '{goal}'.")

def main():
    # Define the directory containing tool descriptions
    examples_dir = os.path.join(os.path.dirname(__file__), "../../schema/examples")
    
    # Load all tools from the examples directory
    tools = load_tools_from_directory(examples_dir)
    if not tools:
        print("⚠️ No tools were loaded. Please check the examples directory.")
        return

    # Test various goals in Spanish and English
    test_goal(tools, "hacer un agujero")
    test_goal(tools, "make a hole")
    test_goal(tools, "necesito traducir texto")
    test_goal(tools, "I need to translate text")

if __name__ == "__main__":
    main() 