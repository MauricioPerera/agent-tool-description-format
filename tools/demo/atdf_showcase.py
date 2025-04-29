#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ATDF Showcase - Demostración interactiva de las capacidades de ATDF.

Este script proporciona una interfaz interactiva para explorar 
las capacidades del formato ATDF (Agent Tool Description Format),
permitiendo al usuario buscar herramientas, ver sus detalles y
probar el agente trilingüe con diferentes consultas.

Ejecute este script desde la línea de comandos para iniciar la demostración.
"""

import os
import sys
import json
import textwrap
from pathlib import Path

# Añadir el directorio raíz al path para importar los módulos
sys.path.append(str(Path(__file__).parent.parent.parent))

# Importar los módulos necesarios
from sdk.atdf_sdk import ATDFTool, ATDFToolbox, load_toolbox_from_directory, find_best_tool
from improved_loader import load_tools_from_directory, select_tool_by_goal, detect_language
from tools.converter import convert_to_enhanced, load_tool, save_tool

class ColorText:
    """Clase para colorear texto en la terminal."""
    # Códigos de color ANSI
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    
    @staticmethod
    def bold(text): return f"{ColorText.BOLD}{text}{ColorText.RESET}"
    
    @staticmethod
    def red(text): return f"{ColorText.RED}{text}{ColorText.RESET}"
    
    @staticmethod
    def green(text): return f"{ColorText.GREEN}{text}{ColorText.RESET}"
    
    @staticmethod
    def yellow(text): return f"{ColorText.YELLOW}{text}{ColorText.RESET}"
    
    @staticmethod
    def blue(text): return f"{ColorText.BLUE}{text}{ColorText.RESET}"
    
    @staticmethod
    def magenta(text): return f"{ColorText.MAGENTA}{text}{ColorText.RESET}"
    
    @staticmethod
    def cyan(text): return f"{ColorText.CYAN}{text}{ColorText.RESET}"

class ATDFShowcase:
    """Clase principal para la demostración de ATDF."""
    
    def __init__(self):
        """Inicializar la demostración."""
        # Configurar directorio de ejemplos
        self.examples_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "schema/examples")
        
        # Verificar que exista el directorio
        if not os.path.exists(self.examples_dir):
            print(f"Error: No se encontró el directorio de ejemplos en '{self.examples_dir}'.")
            sys.exit(1)
        
        # Cargar herramientas
        print(f"Cargando herramientas desde {self.examples_dir}...")
        self.sdk_toolbox = load_toolbox_from_directory(self.examples_dir)
        self.tools = load_tools_from_directory(self.examples_dir)
        
        if len(self.sdk_toolbox) == 0 or len(self.tools) == 0:
            print("Error: No se pudieron cargar las herramientas.")
            sys.exit(1)
        
        print(f"Se cargaron {len(self.sdk_toolbox)} herramientas con el SDK y {len(self.tools)} con el cargador mejorado.\n")
    
    def print_header(self, text):
        """Imprimir un encabezado formateado."""
        width = min(os.get_terminal_size().columns, 80)
        print("\n" + "=" * width)
        print(ColorText.cyan(ColorText.bold(text.center(width))))
        print("=" * width)
    
    def print_section(self, text):
        """Imprimir una sección formateada."""
        width = min(os.get_terminal_size().columns, 80)
        print("\n" + "-" * width)
        print(ColorText.yellow(text))
        print("-" * width)
    
    def print_tool_details(self, tool, language=None):
        """Imprimir los detalles de una herramienta ATDF."""
        # Obtener los datos de la herramienta (puede ser diccionario o ATDFTool)
        if isinstance(tool, ATDFTool):
            tool_data = tool.to_dict()
        else:
            tool_data = tool
        
        # Determinar el idioma a utilizar
        if language is None:
            # Si no se especifica, usar el idioma detectado en la descripción
            language = detect_language(tool_data['description'])
        
        # Obtener versiones localizadas si están disponibles
        description = tool_data['description']
        when_to_use = tool_data['when_to_use']
        
        if 'localization' in tool_data and language in tool_data['localization']:
            description = tool_data['localization'][language].get('description', description)
            when_to_use = tool_data['localization'][language].get('when_to_use', when_to_use)
        
        # Imprimir detalles básicos
        print(f"\n{ColorText.bold('ID:')} {ColorText.green(tool_data['tool_id'])}")
        print(f"{ColorText.bold('Descripción:')} {description}")
        print(f"{ColorText.bold('Cuándo usar:')} {when_to_use}")
        
        # Imprimir parámetros de entrada
        print(f"\n{ColorText.bold('Parámetros de entrada:')}")
        for input_param in tool_data['how_to_use']['inputs']:
            print(f"  - {ColorText.magenta(input_param['name'])} ({ColorText.cyan(input_param['type'])}): {input_param.get('description', 'Sin descripción')}")
        
        # Imprimir salidas
        print(f"\n{ColorText.bold('Salidas:')}")
        print(f"  - {ColorText.bold('Éxito:')} {tool_data['how_to_use']['outputs']['success']}")
        
        print(f"  - {ColorText.bold('Posibles errores:')}")
        for error in tool_data['how_to_use']['outputs']['failure']:
            print(f"    * {ColorText.red(error['code'])}: {error['description']}")
        
        # Imprimir metadatos si están disponibles
        if 'metadata' in tool_data:
            print(f"\n{ColorText.bold('Metadatos:')}")
            for key, value in tool_data['metadata'].items():
                print(f"  - {key}: {value}")
        
        # Imprimir ejemplos si están disponibles
        if 'examples' in tool_data and tool_data['examples']:
            print(f"\n{ColorText.bold('Ejemplos:')}")
            for i, example in enumerate(tool_data['examples'], 1):
                print(f"  {ColorText.bold(f'Ejemplo {i}:')} {example.get('title', 'Sin título')}")
                print(f"    {example.get('description', 'Sin descripción')}")
                
                if 'inputs' in example:
                    print(f"    {ColorText.bold('Entradas:')}")
                    for key, value in example['inputs'].items():
                        print(f"      * {key}: {value}")
        
        # Imprimir información de localización si está disponible
        if 'localization' in tool_data:
            langs = list(tool_data['localization'].keys())
            if langs:
                print(f"\n{ColorText.bold('Idiomas disponibles:')} {', '.join(langs)}")
    
    def menu_principal(self):
        """Mostrar el menú principal."""
        while True:
            self.print_header("ATDF Showcase - Demostración de Agent Tool Description Format")
            
            print(f"\n{ColorText.cyan('Opciones:')}")
            print(f"  1. {ColorText.yellow('Explorar herramientas disponibles')}")
            print(f"  2. {ColorText.yellow('Probar agente trilingüe')}")
            print(f"  3. {ColorText.yellow('Convertir herramienta básica a formato mejorado')}")
            print(f"  4. {ColorText.yellow('Comparar versiones de ATDF')}")
            print(f"  0. {ColorText.red('Salir')}")
            
            choice = input("\nSeleccione una opción (0-4): ")
            
            if choice == '0':
                print("\n¡Gracias por explorar ATDF!")
                sys.exit(0)
            elif choice == '1':
                self.menu_explorar_herramientas()
            elif choice == '2':
                self.menu_probar_agente()
            elif choice == '3':
                self.menu_convertir_herramienta()
            elif choice == '4':
                self.menu_comparar_versiones()
            else:
                print(ColorText.red("\nOpción inválida. Por favor, seleccione una opción válida."))
    
    def menu_explorar_herramientas(self):
        """Menú para explorar las herramientas disponibles."""
        while True:
            self.print_header("Explorar Herramientas ATDF")
            
            # Mostrar lista de herramientas
            print(f"\n{ColorText.cyan('Herramientas disponibles:')}")
            for i, tool in enumerate(self.sdk_toolbox, 1):
                print(f"  {i}. {ColorText.green(tool.tool_id)}: {tool.description[:60]}{'...' if len(tool.description) > 60 else ''}")
            
            print(f"\n{ColorText.cyan('Opciones:')}")
            print(f"  [1-{len(self.sdk_toolbox)}] {ColorText.yellow('Ver detalles de una herramienta')}")
            print(f"  0. {ColorText.red('Volver al menú principal')}")
            
            choice = input("\nSeleccione una opción: ")
            
            if choice == '0':
                return
            elif choice.isdigit() and 1 <= int(choice) <= len(self.sdk_toolbox):
                tool = self.sdk_toolbox[int(choice) - 1]
                
                self.print_section(f"Detalles de la herramienta: {tool.tool_id}")
                self.print_tool_details(tool)
                
                input("\nPresione Enter para continuar...")
            else:
                print(ColorText.red("\nOpción inválida. Por favor, seleccione una opción válida."))
    
    def menu_probar_agente(self):
        """Menú para probar el agente trilingüe."""
        self.print_header("Probar Agente Trilingüe ATDF")
        
        print(f"\n{ColorText.cyan('El agente trilingüe puede detectar el idioma y seleccionar la herramienta adecuada basada en una consulta.')}")
        print(f"{ColorText.cyan('Puede hacer consultas en Español, Inglés o Portugués.')}")
        
        examples = {
            "Español": ["hacer un agujero", "necesito traducir un texto", "herramienta para perforar"],
            "Inglés": ["make a hole", "I need to translate some text", "tool for drilling a wall"],
            "Portugués": ["fazer um furo", "preciso traduzir um texto", "ferramenta para perfurar"]
        }
        
        # Mostrar ejemplos
        print(f"\n{ColorText.yellow('Ejemplos de consultas:')}")
        for language, queries in examples.items():
            print(f"  {ColorText.bold(language)}:")
            for query in queries:
                print(f"    - {query}")
        
        # Bucle para probar consultas
        while True:
            print(f"\n{ColorText.cyan('Opciones:')}")
            print(f"  1. {ColorText.yellow('Escribir una consulta')}")
            print(f"  0. {ColorText.red('Volver al menú principal')}")
            
            choice = input("\nSeleccione una opción (0-1): ")
            
            if choice == '0':
                return
            elif choice == '1':
                # Pedir consulta
                query = input("\nEscriba su consulta: ")
                
                if not query.strip():
                    print(ColorText.red("Consulta vacía. Por favor, ingrese una consulta válida."))
                    continue
                
                # Detectar idioma
                language = detect_language(query)
                language_names = {
                    'es': 'Español',
                    'en': 'Inglés',
                    'pt': 'Portugués'
                }
                
                print(f"\n{ColorText.bold('Idioma detectado:')} {ColorText.blue(language_names.get(language, language))}")
                
                # Seleccionar herramienta
                tool = select_tool_by_goal(self.tools, query)
                
                if tool:
                    print(f"\n{ColorText.bold('Herramienta seleccionada:')} {ColorText.green(tool['tool_id'])}")
                    
                    # Preguntar si mostrar detalles completos
                    show_details = input("\n¿Mostrar detalles completos? (s/n): ").lower().startswith('s')
                    
                    if show_details:
                        self.print_tool_details(tool, language)
                else:
                    print(f"\n{ColorText.red('No se encontró una herramienta adecuada para esta consulta.')}")
                
                input("\nPresione Enter para continuar...")
            else:
                print(ColorText.red("\nOpción inválida. Por favor, seleccione una opción válida."))
    
    def menu_convertir_herramienta(self):
        """Menú para convertir una herramienta básica a formato mejorado."""
        self.print_header("Convertir Herramienta Básica a Formato Mejorado")
        
        # Buscar herramientas básicas (las que no tienen 'enhanced' en el nombre)
        basic_tools = []
        for file in os.listdir(self.examples_dir):
            if file.endswith('.json') and 'enhanced' not in file and not file.endswith('_pt.json') and not file.endswith('_es.json') and not file.endswith('_en.json'):
                basic_tools.append(file)
        
        if not basic_tools:
            print(ColorText.red("\nNo se encontraron herramientas básicas para convertir."))
            input("\nPresione Enter para continuar...")
            return
        
        # Mostrar lista de herramientas básicas
        print(f"\n{ColorText.cyan('Herramientas básicas disponibles:')}")
        for i, tool_file in enumerate(basic_tools, 1):
            print(f"  {i}. {ColorText.green(tool_file)}")
        
        print(f"\n{ColorText.cyan('Opciones:')}")
        print(f"  [1-{len(basic_tools)}] {ColorText.yellow('Convertir una herramienta')}")
        print(f"  0. {ColorText.red('Volver al menú principal')}")
        
        choice = input("\nSeleccione una opción: ")
        
        if choice == '0':
            return
        elif choice.isdigit() and 1 <= int(choice) <= len(basic_tools):
            tool_file = os.path.join(self.examples_dir, basic_tools[int(choice) - 1])
            
            # Cargar herramienta básica
            basic_tool = load_tool(tool_file)
            
            if not basic_tool:
                print(ColorText.red(f"\nNo se pudo cargar la herramienta desde '{tool_file}'."))
                input("\nPresione Enter para continuar...")
                return
            
            # Mostrar herramienta original
            self.print_section("Herramienta Original")
            print(json.dumps(basic_tool, indent=2))
            
            # Convertir a formato mejorado
            author = input("\nAutor para los metadatos (opcional): ") or "ATDF Showcase Demo"
            
            enhanced_tool = convert_to_enhanced(
                basic_tool,
                author=author,
                extract_language=True
            )
            
            # Mostrar herramienta mejorada
            self.print_section("Herramienta Mejorada")
            print(json.dumps(enhanced_tool, indent=2))
            
            # Resaltar lo que se ha añadido
            self.print_section("Campos añadidos")
            
            if 'metadata' in enhanced_tool:
                print(f"{ColorText.green('✓')} {ColorText.bold('Metadatos')}: {len(enhanced_tool['metadata'])} campos")
            
            if 'examples' in enhanced_tool:
                print(f"{ColorText.green('✓')} {ColorText.bold('Ejemplos')}: {len(enhanced_tool['examples'])} ejemplos")
            
            if 'localization' in enhanced_tool:
                langs = list(enhanced_tool['localization'].keys())
                print(f"{ColorText.green('✓')} {ColorText.bold('Localización')}: {len(langs)} idiomas ({', '.join(langs)})")
            
            if 'prerequisites' in enhanced_tool:
                print(f"{ColorText.green('✓')} {ColorText.bold('Prerrequisitos')}: {len(enhanced_tool['prerequisites'])} categorías")
            
            if 'feedback' in enhanced_tool:
                print(f"{ColorText.green('✓')} {ColorText.bold('Feedback')}: {len(enhanced_tool['feedback'])} tipos")
            
            input("\nPresione Enter para continuar...")
        else:
            print(ColorText.red("\nOpción inválida. Por favor, seleccione una opción válida."))
    
    def menu_comparar_versiones(self):
        """Menú para comparar las versiones básica y mejorada de ATDF."""
        self.print_header("Comparar Versiones de ATDF")
        
        basic_schema_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "schema/atdf_schema.json")
        enhanced_schema_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "schema/enhanced_atdf_schema.json")
        
        if not os.path.exists(basic_schema_file) or not os.path.exists(enhanced_schema_file):
            print(ColorText.red("\nNo se encontraron los archivos de esquema."))
            input("\nPresione Enter para continuar...")
            return
        
        try:
            with open(basic_schema_file, 'r', encoding='utf-8') as f:
                basic_schema = json.load(f)
            
            with open(enhanced_schema_file, 'r', encoding='utf-8') as f:
                enhanced_schema = json.load(f)
            
            # Comparar propiedades requeridas
            basic_required = basic_schema.get('required', [])
            enhanced_required = enhanced_schema.get('required', [])
            
            # Comparar propiedades
            basic_properties = set(basic_schema.get('properties', {}).keys())
            enhanced_properties = set(enhanced_schema.get('properties', {}).keys())
            
            new_properties = enhanced_properties - basic_properties
            
            # Mostrar comparación
            self.print_section("Comparación de Versiones ATDF")
            
            print(f"{ColorText.bold('Propiedades requeridas en ATDF básico:')} {', '.join(basic_required)}")
            print(f"{ColorText.bold('Propiedades requeridas en ATDF mejorado:')} {', '.join(enhanced_required)}")
            
            print(f"\n{ColorText.bold('Campos adicionales en ATDF mejorado:')}")
            for prop in sorted(new_properties):
                print(f"  - {ColorText.green(prop)}")
            
            # Mostrar detalles de nuevos campos
            print(f"\n{ColorText.bold('Detalles de nuevos campos:')}")
            for prop in sorted(new_properties):
                if prop in enhanced_schema.get('properties', {}):
                    desc = enhanced_schema['properties'][prop].get('description', 'Sin descripción')
                    print(f"  - {ColorText.green(prop)}: {desc}")
        except Exception as e:
            print(ColorText.red(f"\nError al comparar esquemas: {e}"))
        
        input("\nPresione Enter para continuar...")

# Función principal
def main():
    """Función principal para ejecutar la demostración."""
    try:
        showcase = ATDFShowcase()
        showcase.menu_principal()
    except KeyboardInterrupt:
        print("\n\n¡Gracias por explorar ATDF!")
        sys.exit(0)
    except Exception as e:
        print(f"Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Verificar que se ejecute en una terminal que soporte colores
    if sys.platform == 'win32':
        # En Windows, habilitar colores ANSI
        import os
        os.system('color')
    
    main() 