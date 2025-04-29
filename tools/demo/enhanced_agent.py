#!/usr/bin/env python3
import os
import sys
import argparse
import logging

# Añadir el directorio raíz al path para importar el módulo enhanced_loader
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.enhanced_loader import (
    load_tools_from_directory, 
    select_tool_by_goal,
    get_tool_examples,
    get_tool_prerequisites,
    get_localized_description,
    get_localized_when_to_use
)

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('enhanced_agent')

def print_tool_info(tool, language="es", verbose=False):
    """Mostrar información detallada de una herramienta en el idioma especificado."""
    if not tool:
        if language == "es":
            print("⚠️ No se encontró una herramienta adecuada para el objetivo.")
        elif language == "pt":
            print("⚠️ Não foi encontrada uma ferramenta adequada para o objetivo.")
        else:
            print("⚠️ No suitable tool was found for the goal.")
        return

    # Usar campos localizados si están disponibles
    description = get_localized_description(tool, language)
    when_to_use = get_localized_when_to_use(tool, language)
    
    # Imprimir información básica
    if language == "es":
        print(f"\n🎯 Herramienta seleccionada: {tool['tool_id']}")
        if 'metadata' in tool:
            print(f"📋 Metadata:")
            for key, value in tool['metadata'].items():
                if not key.startswith('_'):  # No mostrar campos internos
                    print(f"  - {key}: {value}")
        print(f"\n➤ ¿Qué hace?: {description}")
        print(f"➤ ¿Cuándo usarla?: {when_to_use}")
        
        # Mostrar prerrequisitos si existen
        prerequisites = get_tool_prerequisites(tool)
        if prerequisites:
            print(f"\n➤ Prerrequisitos:")
            if 'tools' in prerequisites:
                print(f"  - Herramientas necesarias: {', '.join(prerequisites['tools'])}")
            if 'conditions' in prerequisites:
                print(f"  - Condiciones necesarias: {', '.join(prerequisites['conditions'])}")
            if 'permissions' in prerequisites:
                print(f"  - Permisos requeridos: {', '.join(prerequisites['permissions'])}")
        
        print(f"\n➤ ¿Cómo usarla?:")
        print(f"  - Entradas:")
        for input_param in tool['how_to_use']['inputs']:
            if input_param['type'] == 'object' and 'schema' in input_param:
                print(f"    * {input_param['name']} (objeto): {input_param.get('description', 'Sin descripción')}")
                print(f"      Propiedades:")
                for prop_name, prop_details in input_param['schema'].get('properties', {}).items():
                    required = "[Requerido]" if prop_name in input_param['schema'].get('required', []) else ""
                    prop_desc = prop_details.get('description', 'Sin descripción')
                    print(f"        - {prop_name} ({prop_details.get('type', 'indefinido')}): {prop_desc} {required}")
            else:
                print(f"    * {input_param['name']} ({input_param['type']}): {input_param.get('description', 'Sin descripción')}")
        
        print(f"  - Salidas:")
        print(f"    * Éxito: {tool['how_to_use']['outputs']['success']}")
        print(f"    * Posibles errores:")
        for error in tool['how_to_use']['outputs']['failure']:
            print(f"      - {error['code']}: {error['description']}")
        
        # Mostrar información de feedback si existe
        if 'feedback' in tool:
            print(f"\n➤ Feedback durante la operación:")
            if 'progress_indicators' in tool['feedback']:
                print(f"  - Indicadores de progreso: {', '.join(tool['feedback']['progress_indicators'])}")
            if 'completion_signals' in tool['feedback']:
                print(f"  - Señales de completitud: {', '.join(tool['feedback']['completion_signals'])}")
        
        # Mostrar ejemplos si están disponibles y se solicita modo detallado
        if verbose and 'examples' in tool:
            print(f"\n➤ Ejemplos de uso:")
            for i, example in enumerate(tool['examples'], 1):
                print(f"  Ejemplo {i}: {example['title']}")
                print(f"  {example['description']}")
                print(f"  - Entradas:")
                for name, value in example['inputs'].items():
                    if isinstance(value, dict):
                        print(f"    * {name}: {value}")
                    else:
                        print(f"    * {name}: {value}")
                print(f"  - Salida esperada:")
                if isinstance(example['expected_output'], dict):
                    for key, value in example['expected_output'].items():
                        print(f"    * {key}: {value}")
                else:
                    print(f"    * {example['expected_output']}")
                print("")
    
    elif language == "pt":
        print(f"\n🎯 Ferramenta selecionada: {tool['tool_id']}")
        if 'metadata' in tool:
            print(f"📋 Metadata:")
            for key, value in tool['metadata'].items():
                if not key.startswith('_'):
                    print(f"  - {key}: {value}")
        print(f"\n➤ O que faz: {description}")
        print(f"➤ Quando usá-la: {when_to_use}")
        
        prerequisites = get_tool_prerequisites(tool)
        if prerequisites:
            print(f"\n➤ Pré-requisitos:")
            if 'tools' in prerequisites:
                print(f"  - Ferramentas necessárias: {', '.join(prerequisites['tools'])}")
            if 'conditions' in prerequisites:
                print(f"  - Condições necessárias: {', '.join(prerequisites['conditions'])}")
            if 'permissions' in prerequisites:
                print(f"  - Permissões requeridas: {', '.join(prerequisites['permissions'])}")
        
        print(f"\n➤ Como usá-la:")
        print(f"  - Entradas:")
        for input_param in tool['how_to_use']['inputs']:
            if input_param['type'] == 'object' and 'schema' in input_param:
                print(f"    * {input_param['name']} (objeto): {input_param.get('description', 'Sem descrição')}")
                print(f"      Propriedades:")
                for prop_name, prop_details in input_param['schema'].get('properties', {}).items():
                    required = "[Requerido]" if prop_name in input_param['schema'].get('required', []) else ""
                    prop_desc = prop_details.get('description', 'Sem descrição')
                    print(f"        - {prop_name} ({prop_details.get('type', 'indefinido')}): {prop_desc} {required}")
            else:
                print(f"    * {input_param['name']} ({input_param['type']}): {input_param.get('description', 'Sem descrição')}")
        
        print(f"  - Saídas:")
        print(f"    * Sucesso: {tool['how_to_use']['outputs']['success']}")
        print(f"    * Possíveis erros:")
        for error in tool['how_to_use']['outputs']['failure']:
            print(f"      - {error['code']}: {error['description']}")
        
        if 'feedback' in tool:
            print(f"\n➤ Feedback durante a operação:")
            if 'progress_indicators' in tool['feedback']:
                print(f"  - Indicadores de progresso: {', '.join(tool['feedback']['progress_indicators'])}")
            if 'completion_signals' in tool['feedback']:
                print(f"  - Sinais de conclusão: {', '.join(tool['feedback']['completion_signals'])}")
        
        if verbose and 'examples' in tool:
            print(f"\n➤ Exemplos de uso:")
            for i, example in enumerate(tool['examples'], 1):
                print(f"  Exemplo {i}: {example['title']}")
                print(f"  {example['description']}")
                print(f"  - Entradas:")
                for name, value in example['inputs'].items():
                    if isinstance(value, dict):
                        print(f"    * {name}: {value}")
                    else:
                        print(f"    * {name}: {value}")
                print(f"  - Saída esperada:")
                if isinstance(example['expected_output'], dict):
                    for key, value in example['expected_output'].items():
                        print(f"    * {key}: {value}")
                else:
                    print(f"    * {example['expected_output']}")
                print("")
    
    else:  # English by default
        print(f"\n🎯 Selected tool: {tool['tool_id']}")
        if 'metadata' in tool:
            print(f"📋 Metadata:")
            for key, value in tool['metadata'].items():
                if not key.startswith('_'):
                    print(f"  - {key}: {value}")
        print(f"\n➤ What it does: {description}")
        print(f"➤ When to use it: {when_to_use}")
        
        prerequisites = get_tool_prerequisites(tool)
        if prerequisites:
            print(f"\n➤ Prerequisites:")
            if 'tools' in prerequisites:
                print(f"  - Required tools: {', '.join(prerequisites['tools'])}")
            if 'conditions' in prerequisites:
                print(f"  - Required conditions: {', '.join(prerequisites['conditions'])}")
            if 'permissions' in prerequisites:
                print(f"  - Required permissions: {', '.join(prerequisites['permissions'])}")
        
        print(f"\n➤ How to use it:")
        print(f"  - Inputs:")
        for input_param in tool['how_to_use']['inputs']:
            if input_param['type'] == 'object' and 'schema' in input_param:
                print(f"    * {input_param['name']} (object): {input_param.get('description', 'No description')}")
                print(f"      Properties:")
                for prop_name, prop_details in input_param['schema'].get('properties', {}).items():
                    required = "[Required]" if prop_name in input_param['schema'].get('required', []) else ""
                    prop_desc = prop_details.get('description', 'No description')
                    print(f"        - {prop_name} ({prop_details.get('type', 'undefined')}): {prop_desc} {required}")
            else:
                print(f"    * {input_param['name']} ({input_param['type']}): {input_param.get('description', 'No description')}")
        
        print(f"  - Outputs:")
        print(f"    * Success: {tool['how_to_use']['outputs']['success']}")
        print(f"    * Possible errors:")
        for error in tool['how_to_use']['outputs']['failure']:
            print(f"      - {error['code']}: {error['description']}")
        
        if 'feedback' in tool:
            print(f"\n➤ Feedback during operation:")
            if 'progress_indicators' in tool['feedback']:
                print(f"  - Progress indicators: {', '.join(tool['feedback']['progress_indicators'])}")
            if 'completion_signals' in tool['feedback']:
                print(f"  - Completion signals: {', '.join(tool['feedback']['completion_signals'])}")
        
        if verbose and 'examples' in tool:
            print(f"\n➤ Usage examples:")
            for i, example in enumerate(tool['examples'], 1):
                print(f"  Example {i}: {example['title']}")
                print(f"  {example['description']}")
                print(f"  - Inputs:")
                for name, value in example['inputs'].items():
                    if isinstance(value, dict):
                        print(f"    * {name}: {value}")
                    else:
                        print(f"    * {name}: {value}")
                print(f"  - Expected output:")
                if isinstance(example['expected_output'], dict):
                    for key, value in example['expected_output'].items():
                        print(f"    * {key}: {value}")
                else:
                    print(f"    * {example['expected_output']}")
                print("")

def test_goal(tools, goal, language=None, verbose=False):
    """Probar un objetivo y mostrar el resultado."""
    detected_language = language or select_tool_by_goal([], goal).get('_language', 'en')
    language_name = {
        'es': 'ESPAÑOL',
        'en': 'ENGLISH',
        'pt': 'PORTUGUÊS'
    }.get(detected_language, 'UNKNOWN')
    
    print(f"\n=============== {language_name} ===============")
    print(f"Objetivo/Goal/Meta: '{goal}'")
    
    selected_tool = select_tool_by_goal(tools, goal, user_language=language)
    print_tool_info(selected_tool, language=detected_language, verbose=verbose)

def parse_arguments():
    """Parsear argumentos de la línea de comandos."""
    parser = argparse.ArgumentParser(description='Enhanced ATDF Agent Demo')
    parser.add_argument('--goal', type=str, help='Goal to test', default=None)
    parser.add_argument('--language', type=str, choices=['en', 'es', 'pt'], 
                        help='Force language for tool selection', default=None)
    parser.add_argument('--verbose', action='store_true', 
                        help='Show detailed information including examples')
    parser.add_argument('--tool-dir', type=str, 
                        help='Directory containing tool descriptions', 
                        default=None)
    return parser.parse_args()

def main():
    """Función principal del agente mejorado."""
    args = parse_arguments()
    
    # Define the directory containing tool descriptions
    if args.tool_dir:
        examples_dir = args.tool_dir
    else:
        examples_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                                   "schema/examples")
    
    # Load all tools from the examples directory
    tools = load_tools_from_directory(examples_dir)
    if not tools:
        print("⚠️ No tools were loaded. Please check the examples directory.")
        return

    # If a specific goal was provided, test it
    if args.goal:
        test_goal(tools, args.goal, language=args.language, verbose=args.verbose)
        return

    # Otherwise test with several goals in different languages
    print("\n===== TESTING ENHANCED HOLE MAKER =====")
    test_goal(tools, "necesito hacer un agujero preciso en una pared", verbose=args.verbose)
    test_goal(tools, "I need to make a precise hole in a wall", verbose=args.verbose)
    test_goal(tools, "preciso fazer um furo preciso em uma parede", verbose=args.verbose)
    
    print("\n===== TESTING TEXT TRANSLATOR =====")
    test_goal(tools, "necesito traducir un texto", verbose=args.verbose)
    test_goal(tools, "I need to translate some text", verbose=args.verbose)
    test_goal(tools, "preciso traduzir um texto", verbose=args.verbose)

if __name__ == "__main__":
    main() 