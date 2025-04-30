[Home](index.md) | [Especificação](specification.md) | [Exemplos](examples.md) | [Contribuir](contributing.md) | [Multilíngue](multilingual.md) | [Histórico de Alterações](changelog.md) | [Licença](license.md)

**Idiomas:** [English (en)](../en/multilingual.md) | [Español (es)](../es/multilingual.md) | [Português (pt)](multilingual.md)

# Soporte Multilingüe en ATDF

ATDF es un protocolo diseñado para ser neutral respecto al idioma, permitiendo que las descripciones de herramientas se escriban en cualquier idioma. Esta flexibilidad es fundamental para crear agentes de IA que puedan interactuar con usuarios en su idioma nativo.

## Características del Soporte Multilingüe

- **Descripciones en Cualquier Idioma**: El esquema ATDF no impone restricciones sobre el idioma utilizado en los campos de texto como `description`, `when_to_use`, o mensajes de error.
- **Agnóstico al Idioma**: El protocolo funciona de manera idéntica independientemente del idioma utilizado.
- **Coherencia Interna**: Se recomienda que cada descripción de herramienta mantenga coherencia en el idioma usado en todos sus campos.

## Implementación en Sistemas Multilingües

Para sistemas que necesitan soportar múltiples idiomas, recomendamos alguna de las siguientes estrategias:

### 1. Identificadores de Herramientas Neutrales

Mantenga identificadores de herramientas (`tool_id`) que sean neutrales respecto al idioma, mientras que los campos descriptivos pueden variar según el idioma:

```json
// Versión en español
{
  "tool_id": "hole_maker_v1",
  "description": "Permite crear agujeros en superficies sólidas",
  ...
}

// Versión en inglés
{
  "tool_id": "hole_maker_v1",
  "description": "Creates holes in solid surfaces",
  ...
}

// Versión en portugués
{
  "tool_id": "hole_maker_v1",
  "description": "Permite criar furos em superfícies sólidas",
  ...
}
```

### 2. Selección Basada en el Idioma

Los agentes pueden cargar el conjunto de descripciones de herramientas apropiado según el idioma del usuario:

```python
def load_tools_for_language(language_code):
    """Carga herramientas específicas del idioma"""
    directory = f"./tools/{language_code}"
    return load_tools_from_directory(directory)
```

### 3. Coincidencia Semántica

Para agentes que utilizan modelos de lenguaje avanzados, la búsqueda semántica puede permitir encontrar herramientas apropiadas incluso cuando la consulta del usuario está en un idioma diferente al de la descripción de la herramienta:

```python
def select_tool_by_semantic_match(tools, query, model):
    """Selecciona una herramienta mediante coincidencia semántica multilingüe"""
    best_match = None
    highest_score = 0
    
    for tool in tools:
        # El modelo evalúa semánticamente la coincidencia entre la consulta y la descripción
        score = model.semantic_similarity(query, tool["description"])
        if score > highest_score:
            highest_score = score
            best_match = tool
    
    return best_match
```

## Ejemplos Incluidos

Este repositorio incluye ejemplos de descripciones de herramientas en diferentes idiomas:

- Español: `schema/examples/*_es.json`
- Inglés: `schema/examples/*_en.json`
- Portugués: `schema/examples/*_pt.json`

## Detección de Idioma

El módulo `improved_loader.py` incluye una función simple de detección de idioma basada en palabras comunes:

```python
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
```

## Consideraciones para Contribuidores

Si contribuyes con nuevas descripciones de herramientas:

1. Especifica claramente el idioma utilizado (idealmente en el nombre del archivo).
2. Considera proporcionar versiones en múltiples idiomas si es posible.
3. Mantén la coherencia en la terminología dentro de cada idioma.

---

# Multilingual Support in ATDF

ATDF is a protocol designed to be language-neutral, allowing tool descriptions to be written in any language. This flexibility is essential for creating AI agents that can interact with users in their native language.

## Multilingual Support Features

- **Descriptions in Any Language**: The ATDF schema does not impose restrictions on the language used in text fields such as `description`, `when_to_use`, or error messages.
- **Language Agnostic**: The protocol works identically regardless of the language used.
- **Internal Consistency**: It is recommended that each tool description maintains consistency in the language used across all its fields.

## Implementation in Multilingual Systems

For systems that need to support multiple languages, we recommend one of the following strategies:

### 1. Language-Neutral Tool Identifiers

Maintain tool identifiers (`tool_id`) that are language-neutral, while descriptive fields can vary by language:

```json
// Spanish version
{
  "tool_id": "hole_maker_v1",
  "description": "Permite crear agujeros en superficies sólidas",
  ...
}

// English version
{
  "tool_id": "hole_maker_v1",
  "description": "Creates holes in solid surfaces",
  ...
}

// Portuguese version
{
  "tool_id": "hole_maker_v1",
  "description": "Permite criar furos em superfícies sólidas",
  ...
}
```

### 2. Language-Based Selection

Agents can load the appropriate set of tool descriptions based on the user's language:

```python
def load_tools_for_language(language_code):
    """Load language-specific tools"""
    directory = f"./tools/{language_code}"
    return load_tools_from_directory(directory)
```

### 3. Semantic Matching

For agents using advanced language models, semantic search can allow finding appropriate tools even when the user's query is in a different language than the tool description:

```python
def select_tool_by_semantic_match(tools, query, model):
    """Select a tool using multilingual semantic matching"""
    best_match = None
    highest_score = 0
    
    for tool in tools:
        # The model semantically evaluates the match between query and description
        score = model.semantic_similarity(query, tool["description"])
        if score > highest_score:
            highest_score = score
            best_match = tool
    
    return best_match
```

## Included Examples

This repository includes examples of tool descriptions in different languages:

- Spanish: `schema/examples/*_es.json`
- English: `schema/examples/*_en.json`
- Portuguese: `schema/examples/*_pt.json`

## Language Detection

The `improved_loader.py` module includes a simple language detection function based on common words:

```python
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
```

## Considerations for Contributors

If you contribute new tool descriptions:

1. Clearly specify the language used (ideally in the filename).
2. Consider providing versions in multiple languages if possible.
3. Maintain consistency in terminology within each language.

---

# Suporte Multilíngue no ATDF

O ATDF é um protocolo projetado para ser neutro em relação ao idioma, permitindo que as descrições de ferramentas sejam escritas em qualquer idioma. Essa flexibilidade é essencial para criar agentes de IA que possam interagir com usuários em seu idioma nativo.

## Características do Suporte Multilíngue

- **Descrições em Qualquer Idioma**: O esquema ATDF não impõe restrições sobre o idioma utilizado em campos de texto como `description`, `when_to_use`, ou mensagens de erro.
- **Agnóstico ao Idioma**: O protocolo funciona de maneira idêntica independentemente do idioma utilizado.
- **Coerência Interna**: Recomenda-se que cada descrição de ferramenta mantenha coerência no idioma usado em todos os seus campos.

## Implementação em Sistemas Multilíngues

Para sistemas que precisam suportar múltiplos idiomas, recomendamos uma das seguintes estratégias:

### 1. Identificadores de Ferramentas Neutros

Mantenha identificadores de ferramentas (`tool_id`) que sejam neutros em relação ao idioma, enquanto os campos descritivos podem variar de acordo com o idioma:

```json
// Versão em espanhol
{
  "tool_id": "hole_maker_v1",
  "description": "Permite crear agujeros en superficies sólidas",
  ...
}

// Versão em inglês
{
  "tool_id": "hole_maker_v1",
  "description": "Creates holes in solid surfaces",
  ...
}

// Versão em português
{
  "tool_id": "hole_maker_v1",
  "description": "Permite criar furos em superfícies sólidas",
  ...
}
```

### 2. Seleção Baseada no Idioma

Os agentes podem carregar o conjunto de descrições de ferramentas apropriado de acordo com o idioma do usuário:

```python
def load_tools_for_language(language_code):
    """Carrega ferramentas específicas do idioma"""
    directory = f"./tools/{language_code}"
    return load_tools_from_directory(directory)
```

### 3. Correspondência Semântica

Para agentes que utilizam modelos de linguagem avançados, a busca semântica pode permitir encontrar ferramentas apropriadas mesmo quando a consulta do usuário está em um idioma diferente do da descrição da ferramenta:

```python
def select_tool_by_semantic_match(tools, query, model):
    """Seleciona uma ferramenta usando correspondência semântica multilíngue"""
    best_match = None
    highest_score = 0
    
    for tool in tools:
        # O modelo avalia semanticamente a correspondência entre a consulta e a descrição
        score = model.semantic_similarity(query, tool["description"])
        if score > highest_score:
            highest_score = score
            best_match = tool
    
    return best_match
```

## Exemplos Incluídos

Este repositório inclui exemplos de descrições de ferramentas em diferentes idiomas:

- Espanhol: `schema/examples/*_es.json`
- Inglês: `schema/examples/*_en.json`
- Português: `schema/examples/*_pt.json`

## Detecção de Idioma

O módulo `improved_loader.py` inclui uma função simples de detecção de idioma baseada em palavras comuns:

```python
def detect_language(text):
    """Detecção simples de idioma baseada em palavras comuns."""
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
```

## Considerações para Contribuidores

Se você contribuir com novas descrições de ferramentas:

1. Especifique claramente o idioma utilizado (idealmente no nome do arquivo).
2. Considere fornecer versões em múltiplos idiomas, se possível.
3. Mantenha a coerência na terminologia dentro de cada idioma. 