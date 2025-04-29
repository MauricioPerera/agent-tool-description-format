#!/usr/bin/env python3
"""
ATDF Converter - Transforma descripciones ATDF del formato antiguo al formato extendido.

Este script permite convertir descripciones de herramientas en formato ATDF 0.1.0
al formato extendido ATDF 0.2.0, manteniendo compatibilidad y añadiendo campos
opcionales para aprovechar las nuevas características.
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('atdf_converter')

def load_tool(filepath):
    """Cargar una descripción de herramienta desde un archivo JSON."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Error: Archivo '{filepath}' no encontrado.")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Error: JSON inválido en '{filepath}': {e}")
        return None

def save_tool(tool, output_path):
    """Guardar una descripción de herramienta en un archivo JSON."""
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(tool, f, indent=2, ensure_ascii=False)
        logger.info(f"Herramienta guardada exitosamente en '{output_path}'")
        return True
    except Exception as e:
        logger.error(f"Error al guardar la herramienta en '{output_path}': {e}")
        return False

def convert_to_enhanced(tool, author=None, extract_language=True):
    """Convertir una herramienta del formato básico al formato mejorado."""
    if not tool:
        return None

    # Crear una copia para no modificar el original
    enhanced_tool = tool.copy()

    # 1. Añadir metadatos si no existen
    if 'metadata' not in enhanced_tool:
        enhanced_tool['metadata'] = {
            "version": "1.0.0",
            "author": author or "ATDF Converter",
            "created_at": datetime.now().strftime("%Y-%m-%d"),
            "updated_at": datetime.now().strftime("%Y-%m-%d")
        }
        
        # Intentar generar tags a partir de la descripción y when_to_use
        text = enhanced_tool.get('description', '') + ' ' + enhanced_tool.get('when_to_use', '')
        
        # Identificar posibles tags
        common_tags = [
            # Herramientas físicas
            "herramienta_física", "perforación", "corte", "medición", "fijación",
            # Herramientas digitales
            "herramienta_digital", "procesamiento", "análisis", "comunicación",
            # Acciones comunes
            "creación", "transformación", "conexión", "visualización"
        ]
        
        tags = []
        for tag in common_tags:
            if tag.lower() in text.lower() or tag.replace('_', ' ').lower() in text.lower():
                tags.append(tag)
        
        # Inferir categoría principal
        if any(tag in ['herramienta_física', 'perforación', 'corte', 'medición'] for tag in tags):
            category = "herramientas_físicas"
        elif any(tag in ['herramienta_digital', 'procesamiento', 'análisis'] for tag in tags):
            category = "herramientas_digitales"
        else:
            category = "herramientas_generales"
            
        enhanced_tool['metadata']["tags"] = tags
        enhanced_tool['metadata']["category"] = category

    # 2. Añadir localización si se infiere un idioma
    if extract_language and 'localization' not in enhanced_tool:
        # Detectar idioma de la descripción original
        detected_language = detect_language(enhanced_tool.get('description', ''))
        
        # Si no es inglés, añadir localización
        if detected_language != 'en':
            enhanced_tool['localization'] = {
                detected_language: {
                    "description": enhanced_tool.get('description', ''),
                    "when_to_use": enhanced_tool.get('when_to_use', '')
                },
                "en": {
                    "description": auto_translate(enhanced_tool.get('description', ''), 
                                                detected_language, 'en'),
                    "when_to_use": auto_translate(enhanced_tool.get('when_to_use', ''), 
                                                detected_language, 'en')
                }
            }
        else:
            # Si es inglés, mantener inglés y añadir español como ejemplo
            enhanced_tool['localization'] = {
                "en": {
                    "description": enhanced_tool.get('description', ''),
                    "when_to_use": enhanced_tool.get('when_to_use', '')
                },
                "es": {
                    "description": auto_translate(enhanced_tool.get('description', ''), 'en', 'es'),
                    "when_to_use": auto_translate(enhanced_tool.get('when_to_use', ''), 'en', 'es')
                }
            }

    # 3. Crear secciones de prerrequisitos y feedback si son apropiadas
    if detect_is_physical_tool(enhanced_tool):
        if 'prerequisites' not in enhanced_tool:
            enhanced_tool['prerequisites'] = {
                "tools": [],
                "conditions": ["entorno_seguro"],
                "permissions": []
            }
        
        if 'feedback' not in enhanced_tool:
            enhanced_tool['feedback'] = {
                "progress_indicators": ["operacion_en_curso"],
                "completion_signals": ["operacion_completada"]
            }
    
    # 4. Añadir sección de ejemplos básica
    if 'examples' not in enhanced_tool and 'how_to_use' in enhanced_tool:
        enhanced_tool['examples'] = generate_examples(enhanced_tool)
    
    # 5. Mejorar descripciones de entradas si son genéricas
    enhance_input_descriptions(enhanced_tool)
    
    return enhanced_tool

def detect_language(text):
    """Detecta el idioma de un texto usando heurísticas simples."""
    # Palabras comunes en diferentes idiomas
    es_markers = ['hacer', 'crear', 'usar', 'cuando', 'necesites', 'agujero', 'traducir', 'permite']
    en_markers = ['make', 'create', 'use', 'when', 'need', 'hole', 'translate', 'allows']
    pt_markers = ['fazer', 'criar', 'usar', 'quando', 'precisar', 'furo', 'traduzir', 'permite']
    
    es_count = sum(1 for word in es_markers if word in text.lower())
    en_count = sum(1 for word in en_markers if word in text.lower())
    pt_count = sum(1 for word in pt_markers if word in text.lower())
    
    if es_count > en_count and es_count > pt_count:
        return 'es'
    elif pt_count > en_count and pt_count > es_count:
        return 'pt'
    else:
        return 'en'

def auto_translate(text, source_lang, target_lang):
    """Simula una traducción automática (en un sistema real usaríamos una API de traducción)."""
    # Esta es una versión simplificada para demostración
    # En un sistema real, conectaríamos con un servicio de traducción
    
    simple_translations = {
        # Español a inglés
        ('es', 'en'): {
            'Permite crear agujeros en superficies sólidas': 'Creates holes in solid surfaces',
            'Usar cuando necesites generar un agujero en una pared': 'Use when you need to make a hole in a wall',
            'Permite traducir texto entre idiomas': 'Translates text between languages',
            'Usar cuando necesites convertir texto de un idioma a otro': 'Use when you need to convert text from one language to another'
        },
        # Inglés a español
        ('en', 'es'): {
            'Creates holes in solid surfaces': 'Permite crear agujeros en superficies sólidas',
            'Use when you need to make a hole in a wall': 'Usar cuando necesites generar un agujero en una pared',
            'Translates text between languages': 'Permite traducir texto entre idiomas',
            'Use when you need to convert text from one language to another': 'Usar cuando necesites convertir texto de un idioma a otro'
        }
    }
    
    key = (source_lang, target_lang)
    
    if key in simple_translations and text in simple_translations[key]:
        return simple_translations[key][text]
    
    # Si no tenemos una traducción específica, devolvemos el texto original
    # con una indicación de que es una traducción provisional
    return f"[{text}]" # En un sistema real retornaríamos una traducción

def detect_is_physical_tool(tool):
    """Detecta si la herramienta parece ser física basándose en su descripción."""
    physical_indicators = [
        'agujero', 'taladro', 'perforar', 'superficie', 'martillo', 'cortar',
        'físic', 'material', 'hole', 'drill', 'hammer', 'cut', 'surface',
        'physical', 'furo', 'perfurar', 'superfície', 'martelo', 'cortar'
    ]
    
    description = tool.get('description', '').lower()
    when_to_use = tool.get('when_to_use', '').lower()
    full_text = description + ' ' + when_to_use
    
    # Si hay metadatos, verificar categoría y tags
    if 'metadata' in tool:
        metadata = tool['metadata']
        if 'category' in metadata and 'física' in metadata['category'].lower():
            return True
        if 'tags' in metadata:
            tags = [tag.lower() for tag in metadata['tags']]
            if any(indicator in tag for indicator in physical_indicators for tag in tags):
                return True
    
    # Verificar si hay indicadores físicos en el texto
    return any(indicator in full_text for indicator in physical_indicators)

def generate_examples(tool):
    """Genera ejemplos básicos para una herramienta."""
    examples = []
    
    # Solo podemos generar ejemplos si tenemos información sobre entradas/salidas
    if 'how_to_use' not in tool or 'inputs' not in tool['how_to_use']:
        return examples
    
    # Crear un ejemplo de uso exitoso
    inputs = {}
    for input_param in tool['how_to_use']['inputs']:
        # Generar un valor de ejemplo según el tipo
        name = input_param['name']
        param_type = input_param['type']
        
        if param_type == 'string':
            inputs[name] = f"ejemplo_{name}"
        elif param_type == 'number':
            inputs[name] = 10
        elif param_type == 'boolean':
            inputs[name] = True
        elif param_type == 'object' and 'schema' in input_param:
            # Para objetos, crear un ejemplo con los campos requeridos
            obj = {}
            schema = input_param['schema']
            for prop_name, prop_details in schema.get('properties', {}).items():
                if prop_details.get('type') == 'string':
                    obj[prop_name] = f"ejemplo_{prop_name}"
                elif prop_details.get('type') == 'number':
                    obj[prop_name] = 5
                elif prop_details.get('type') == 'boolean':
                    obj[prop_name] = True
            inputs[name] = obj
    
    # Ejemplo de éxito
    success_example = {
        "title": "Ejemplo básico de uso exitoso",
        "description": f"Uso básico de la herramienta {tool['tool_id']}",
        "inputs": inputs,
        "expected_output": tool['how_to_use']['outputs']['success']
    }
    examples.append(success_example)
    
    # Ejemplo de error si hay errores definidos
    if tool['how_to_use']['outputs']['failure'] and len(tool['how_to_use']['outputs']['failure']) > 0:
        error = tool['how_to_use']['outputs']['failure'][0]
        error_example = {
            "title": "Ejemplo de error",
            "description": f"Ejemplo que muestra un error típico: {error['code']}",
            "inputs": inputs,  # Usamos los mismos inputs por simplicidad
            "expected_output": {
                "error": error['code'],
                "message": error['description']
            }
        }
        examples.append(error_example)
    
    return examples

def enhance_input_descriptions(tool):
    """Mejora las descripciones de las entradas si son genéricas o faltantes."""
    if 'how_to_use' not in tool or 'inputs' not in tool['how_to_use']:
        return
    
    for input_param in tool['how_to_use']['inputs']:
        if 'description' not in input_param or not input_param['description']:
            name = input_param['name']
            param_type = input_param['type']
            
            # Generar una descripción por defecto
            input_param['description'] = f"Parámetro de entrada '{name}' de tipo {param_type}"

def main():
    """Función principal para la línea de comandos."""
    parser = argparse.ArgumentParser(description="Conversor de formato ATDF 0.1.0 a formato extendido ATDF 0.2.0")
    parser.add_argument("--input", "-i", help="Archivo JSON con la descripción ATDF original", required=True)
    parser.add_argument("--output", "-o", help="Ruta para guardar la versión mejorada (por defecto: [input]_enhanced.json)")
    parser.add_argument("--author", "-a", help="Nombre del autor para los metadatos (opcional)")
    parser.add_argument("--no-translate", action="store_true", help="Desactivar la generación de traducciones")
    
    args = parser.parse_args()
    
    # Determinar ruta de salida si no se especificó
    if not args.output:
        base, ext = os.path.splitext(args.input)
        args.output = f"{base}_enhanced{ext}"
    
    # Cargar la herramienta original
    tool = load_tool(args.input)
    if not tool:
        sys.exit(1)
    
    # Convertir al formato mejorado
    enhanced_tool = convert_to_enhanced(tool, args.author, not args.no_translate)
    if not enhanced_tool:
        logger.error("Error al convertir la herramienta.")
        sys.exit(1)
    
    # Guardar la herramienta mejorada
    if save_tool(enhanced_tool, args.output):
        print(f"✅ Conversión exitosa: {args.input} → {args.output}")
    else:
        logger.error("Error al guardar la herramienta convertida.")
        sys.exit(1)

if __name__ == "__main__":
    main() 