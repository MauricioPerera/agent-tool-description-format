import os
from loader import load_tools_from_directory, select_tool_by_goal


def main():
    # Define the directory containing tool descriptions
    examples_dir = os.path.join(os.path.dirname(__file__), "../../schema/examples")

    # Load all tools from the examples directory
    tools = load_tools_from_directory(examples_dir)
    if not tools:
        print("⚠️ No tools were loaded. Please check the examples directory.")
        return

    # Define a sample goal
    goal = "hacer un agujero"  # Example goal; could be user input in a real application

    # Select a tool based on the goal
    selected_tool = select_tool_by_goal(tools, goal)

    # Display results
    if selected_tool:
        print(f"\n🎯 Herramienta seleccionada: {selected_tool['tool_id']}\n")
        print(f"➤ ¿Qué hace?: {selected_tool['description']}")
        print(f"➤ ¿Cuándo usarla?: {selected_tool['when_to_use']}")
        print(f"➤ ¿Cómo usarla?:")
        print(f"  - Entradas:")
        for input_param in selected_tool["how_to_use"]["inputs"]:
            print(
                f"    * {input_param['name']} ({input_param['type']}): {input_param.get('description', 'Sin descripción')}"
            )
        print(f"  - Salidas:")
        print(f"    * Éxito: {selected_tool['how_to_use']['outputs']['success']}")
        print(f"    * Posibles errores:")
        for error in selected_tool["how_to_use"]["outputs"]["failure"]:
            print(f"      - {error['code']}: {error['description']}")
    else:
        print(f"⚠️ No se encontró una herramienta adecuada para el objetivo: '{goal}'.")


if __name__ == "__main__":
    main()
