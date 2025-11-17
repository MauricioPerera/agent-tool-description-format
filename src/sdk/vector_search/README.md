# Búsqueda Vectorial para ATDF en Python

Este módulo proporciona soporte para búsqueda semántica de herramientas ATDF utilizando bases de datos vectoriales ligeras y embebidas.

## 📦 Instalación

Esta funcionalidad es opcional y requiere dependencias adicionales:

```bash
pip install lancedb sentence-transformers
```

## 🔍 Uso Básico

```python
import asyncio
from sdk.atdf_sdk import ATDFToolbox, load_toolbox_from_directory
from sdk.vector_search import ATDFVectorStore

async def main():
    # 1. Crear e inicializar el almacén vectorial
    vector_store = ATDFVectorStore()
    await vector_store.initialize()
    
    # 2. Crear un toolbox con el almacén vectorial
    toolbox = ATDFToolbox({'vector_store': vector_store})
    
    # O alternativamente, añadir el almacén a un toolbox existente
    # toolbox = load_toolbox_from_directory('./tools')
    # toolbox.set_vector_store(vector_store)
    
    # 3. Cargar herramientas
    toolbox.load_tools_from_directory('./tools')
    
    # 4. Realizar una búsqueda vectorial
    results = toolbox.find_tools_by_text(
        'comunicarme con alguien',
        language='es',
        use_vector_search=True
    )
    
    # Mostrar resultados
    for i, (tool, score) in enumerate(results):
        print(f"{i+1}. {tool.tool_id} (score: {score:.2f}) - {tool.description}")

    # Si necesitas compatibilidad con código que espera solo herramientas
    legacy_results = toolbox.find_tools_by_text(
        'comunicarme con alguien',
        language='es',
        use_vector_search=True,
        return_scores=False,
    )
    for tool in legacy_results:
        print(f"{tool.tool_id} - {tool.description}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 🎮 API Completa

### ATDFVectorStore

```python
# Crear el almacén vectorial
vector_store = ATDFVectorStore(
    db_path="ruta/a/directorio",     # Ubicación de la BD (por defecto: "atdf_vector_db")
    table_name="nombre_tabla",       # Nombre de la tabla (por defecto: "tools")
    model_name="modelo_embeddings"   # Modelo a usar (por defecto: "sentence-transformers/all-MiniLM-L6-v2")
)

# Inicializar (conectar a BD y cargar modelo)
await vector_store.initialize()

# Crear BD a partir de herramientas
await vector_store.create_from_tools(toolbox.tools)

# Añadir una herramienta individual
await vector_store.add_tool(tool)

# Búsqueda avanzada
results = await vector_store.search_tools(
    query="consulta de búsqueda",
    options={
        "language": "es",            # Filtrar por idioma
        "category": "comunicación",  # Filtrar por categoría
        "limit": 5                   # Número máximo de resultados
    }
)

# Encontrar la mejor herramienta
best_tool = await vector_store.find_best_tool(
    goal="enviar correo electrónico",
    options={"language": "es"}
)
```

### Integración con ATDFToolbox

```python
# Método 1: En la creación del toolbox
toolbox = ATDFToolbox({'vector_store': vector_store})

# Método 2: Después de crear el toolbox
toolbox.set_vector_store(vector_store)

# Uso en búsqueda de herramientas (recuperando herramienta y puntuación)
results = toolbox.find_tools_by_text("consulta", use_vector_search=True)

# O bien, obtener solo herramientas para código heredado
legacy_results = toolbox.find_tools_by_text(
    "consulta",
    use_vector_search=True,
    return_scores=False,
)

# Uso en selección automática
best_tool = toolbox.select_tool_for_task("objetivo", use_vector_search=True)

# Con la función auxiliar
from sdk.atdf_sdk import find_best_tool
best_tool = find_best_tool(toolbox, "objetivo", use_vector_search=True)
```

## 📈 Rendimiento

- **Memoria**: ~100-1GB (dependiendo del modelo de embeddings)
- **Almacenamiento**: ~10-20MB para 1000 herramientas
- **Velocidad**:
  - Inicialización: 1-3 segundos
  - Generación de embeddings: ~50-200ms por herramienta
  - Búsqueda: 5-20ms para colecciones de hasta 10,000 herramientas

## 🚀 Ejemplo Completo

Ejecuta el ejemplo incluido:

```bash
python -m sdk.vector_search.example
```

Este ejemplo muestra:
- Configuración del almacén vectorial
- Carga e indexación de herramientas
- Comparación de búsqueda regular vs vectorial
- Búsqueda semántica avanzada 