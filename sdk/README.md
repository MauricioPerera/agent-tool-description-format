# ATDF SDK

El SDK de ATDF (Agent Tool Description Format) proporciona una interfaz sencilla para integrar herramientas ATDF en agentes de IA. Este SDK facilita la carga, búsqueda y utilización de herramientas descritas en formato ATDF.

## Características principales

- **Compatibilidad con ambas versiones**: Soporte para herramientas ATDF en formato básico (v0.1.0) y extendido (v0.2.0).
- **Carga automática de herramientas**: Importación de herramientas desde archivos individuales o directorios completos.
- **Búsqueda inteligente**: Búsqueda de herramientas por texto con soporte multilingüe.
- **Selección automatizada**: Capacidad para seleccionar automáticamente la herramienta más adecuada para una tarea.
- **Soporte para múltiples idiomas**: Utilización de herramientas en diferentes idiomas.
- **Extracción de esquemas**: Generación de esquemas JSON para validar entradas de herramientas.

## Instalación

El SDK de ATDF está incluido en este repositorio, no requiere instalación adicional:

```python
from sdk.atdf_sdk import ATDFTool, ATDFToolbox, load_toolbox_from_directory, find_best_tool
```

## Uso básico

### Cargar herramientas

```python
# Cargar todas las herramientas desde un directorio
toolbox = load_toolbox_from_directory("schema/examples")

# Cargar una herramienta específica
toolbox = ATDFToolbox()
toolbox.load_tool_from_file("schema/examples/hole_maker.json")
```

### Buscar herramientas

```python
# Buscar herramientas por texto
herramientas = toolbox.find_tools_by_text("hacer un agujero", language="es")
for herramienta in herramientas:
    print(f"- {herramienta.tool_id}: {herramienta.description}")
```

### Seleccionar herramienta para una tarea

```python
# Encontrar la mejor herramienta para una tarea
tarea = "Necesito traducir un texto del inglés al español"
herramienta = find_best_tool(toolbox, tarea, language="es")

if herramienta:
    print(f"Herramienta recomendada: {herramienta.tool_id}")
    print(f"Descripción: {herramienta.description}")
    print(f"Cuando usar: {herramienta.when_to_use}")
else:
    print("No se encontró una herramienta adecuada para esta tarea.")
```

### Acceder a los detalles de una herramienta

```python
# Obtener una herramienta por su ID
herramienta = toolbox.get_tool("text_translator_v1")

if herramienta:
    # Acceder a propiedades básicas
    print(f"ID: {herramienta.tool_id}")
    print(f"Descripción: {herramienta.description}")
    
    # Acceder a parámetros de entrada
    print("Parámetros de entrada:")
    for input_param in herramienta.inputs:
        print(f"- {input_param['name']} ({input_param['type']}): {input_param.get('description', '')}")
    
    # Acceder a metadatos extendidos (si están disponibles)
    if herramienta.metadata:
        print(f"Versión: {herramienta.metadata.get('version', 'N/A')}")
        print(f"Autor: {herramienta.metadata.get('author', 'N/A')}")
    
    # Acceder a ejemplos (si están disponibles)
    if herramienta.examples:
        print("Ejemplos de uso:")
        for ejemplo in herramienta.examples:
            print(f"- {ejemplo.get('title', 'Sin título')}")
```

## Características avanzadas

### Generar esquema JSON para validar entradas

```python
import json

# Obtener el esquema JSON para validar entradas
herramienta = toolbox.get_tool("hole_maker_v1")
esquema = herramienta.get_input_schema()

# Imprimir el esquema JSON con formato
print(json.dumps(esquema, indent=2))
```

### Soporte multilingüe

```python
# Cargar herramientas
toolbox = load_toolbox_from_directory("schema/examples")

# Obtener una herramienta
herramienta = toolbox.get_tool("hole_maker_v1")

# Verificar idiomas soportados
idiomas = herramienta.supported_languages
print(f"Idiomas disponibles: {', '.join(idiomas)}")

# Obtener descripción en diferentes idiomas
print(f"Descripción (ES): {herramienta.description}")
print(f"Descripción (EN): {herramienta.description('en')}")
print(f"Descripción (PT): {herramienta.description('pt')}")
```

## Ejemplo completo

```python
from sdk.atdf_sdk import load_toolbox_from_directory, find_best_tool

# Cargar todas las herramientas
toolbox = load_toolbox_from_directory("schema/examples", recursive=True)
print(f"Se cargaron {len(toolbox)} herramientas")

# Analizar una petición del usuario
peticion_usuario = "Necesito hacer un agujero en la pared para colgar un cuadro"
idioma_detectado = "es"  # En un caso real, esto se detectaría automáticamente

# Encontrar la herramienta más adecuada
herramienta = find_best_tool(toolbox, peticion_usuario, language=idioma_detectado)

if herramienta:
    print(f"\nHerramienta seleccionada: {herramienta.tool_id}")
    print(f"Descripción: {herramienta.description}")
    
    # Verificar prerrequisitos
    if herramienta.prerequisites:
        print("\nPrerrequisitos:")
        for categoria, items in herramienta.prerequisites.items():
            print(f"- {categoria}:")
            for item in items:
                print(f"  * {item}")
    
    # Mostrar ejemplos
    if herramienta.examples:
        print("\nEjemplos de uso:")
        for ejemplo in herramienta.examples:
            print(f"- {ejemplo.get('title')}: {ejemplo.get('description')}")
```

## Contribuir

Si deseas contribuir al desarrollo del SDK de ATDF, puedes hacerlo a través de pull requests en este repositorio. Asegúrate de seguir las convenciones de código y añadir pruebas para las nuevas funcionalidades.

## Licencia

Este proyecto está licenciado bajo los mismos términos que el proyecto principal ATDF. 