# ATDF Showcase - Demostración interactiva

Esta herramienta proporciona una interfaz interactiva para explorar las capacidades del formato ATDF (Agent Tool Description Format).

## Características

- Exploración de herramientas ATDF disponibles
- Prueba del agente trilingüe (español, inglés, portugués)
- Conversión de herramientas básicas al formato mejorado
- Comparación de las diferentes versiones del esquema ATDF

## Requisitos

- Python 3.7 o superior
- Acceso a los módulos de ATDF (SDK, cargador mejorado, conversor)

## Uso

Para iniciar la demostración, ejecute el siguiente comando desde el directorio raíz del proyecto:

```bash
python tools/demo/atdf_showcase.py
```

## Navegación

El programa utiliza una interfaz de texto interactiva con menús numerados. Use los números correspondientes para navegar entre las diferentes opciones:

1. **Explorar herramientas disponibles** - Ver detalles de las herramientas ATDF en el sistema
2. **Probar agente trilingüe** - Realizar consultas en distintos idiomas para ver cómo el sistema selecciona herramientas
3. **Convertir herramienta básica a formato mejorado** - Ver el proceso de conversión en acción
4. **Comparar versiones de ATDF** - Ver las diferencias entre el esquema básico y el mejorado

## Ejemplos de consultas

### Español
- "hacer un agujero"
- "necesito traducir un texto"
- "herramienta para perforar"

### Inglés
- "make a hole"
- "I need to translate some text"
- "tool for drilling a wall"

### Portugués
- "fazer um furo"
- "preciso traduzir um texto"
- "ferramenta para perfurar"

## Visualización

La herramienta utiliza colores ANSI para mejorar la legibilidad en la terminal. Asegúrese de que su terminal admita colores para una mejor experiencia.

---

Esta demostración es parte del proyecto ATDF (Agent Tool Description Format), un formato estandarizado para describir herramientas que pueden ser utilizadas por agentes de IA. 