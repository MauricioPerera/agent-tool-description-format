**Languages:** [English (en)](enhancement_proposal.md) | [Español (es)](../es/enhancement_proposal.md) | [Português (pt)](../pt/enhancement_proposal.md)

# Propuestas de Mejora para ATDF

## Extensiones Recomendadas

### 1. Campos de Metadatos Opcionales
```json
{
  "metadata": {
    "version": "1.0.0",
    "author": "Nombre del autor",
    "tags": ["física", "perforación", "construcción"],
    "category": "herramientas_físicas",
    "created_at": "2023-11-15",
    "updated_at": "2025-02-20"
  }
}
```

**Beneficios**: 
- Facilita la categorización y búsqueda de herramientas
- Mejora la organización en grandes colecciones de herramientas
- Permite filtrado por categoría, fecha o autor

### 2. Soporte para Tipos Complejos de Entrada/Salida
```json
{
  "how_to_use": {
    "inputs": [
      {
        "name": "configuration",
        "type": "object",
        "schema": {
          "properties": {
            "depth": {"type": "number"},
            "angle": {"type": "number"},
            "mode": {"type": "string", "enum": ["normal", "turbo"]}
          },
          "required": ["depth"]
        },
        "description": "Configuración detallada del agujero"
      }
    ]
  }
}
```

**Beneficios**:
- Permite describir estructuras de datos complejas
- Mejora la validación de entradas
- Facilita la integración con APIs modernas

### 3. Ejemplos de Uso Integrados
```json
{
  "examples": [
    {
      "title": "Perforar pared de yeso",
      "description": "Ejemplo básico de perforación en pared",
      "inputs": {
        "location": "x:10,y:20",
        "bit_id": "BIT_5MM"
      },
      "expected_output": "Agujero creado con éxito"
    },
    {
      "title": "Perforar superficie no compatible",
      "description": "Ejemplo de manejo de error",
      "inputs": {
        "location": "x:30,y:15",
        "bit_id": "BIT_10MM"
      },
      "expected_output": {
        "error": "invalid_surface",
        "message": "La superficie no es perforable"
      }
    }
  ]
}
```

**Beneficios**:
- Proporciona contexto real para el uso de la herramienta
- Facilita el aprendizaje para agentes de IA
- Sirve como documentación integrada

### 4. Sistema de Prerequisitos y Dependencias
```json
{
  "prerequisites": {
    "tools": ["superficie_plana_v1", "marcador_v2"],
    "conditions": ["superficie_seca", "no_circulacion_electrica"],
    "permissions": ["manipulacion_estructural"]
  }
}
```

**Beneficios**:
- Permite a los agentes verificar requisitos previos
- Mejora la seguridad al especificar condiciones necesarias
- Facilita el encadenamiento de herramientas

### 5. Feedback y Monitoreo
```json
{
  "feedback": {
    "progress_indicators": ["vibracion", "temperatura", "sonido"],
    "completion_signals": ["ausencia_resistencia", "profundidad_alcanzada"]
  }
}
```

**Beneficios**:
- Permite a los agentes monitorear el progreso
- Mejora la detección de completitud de tareas
- Importante para herramientas físicas con ejecución prolongada

### 6. Localización Mejorada
```json
{
  "localization": {
    "es": {
      "description": "Permite crear agujeros en superficies sólidas",
      "when_to_use": "Usar cuando necesites generar un agujero en una pared"
    },
    "en": {
      "description": "Creates holes in solid surfaces",
      "when_to_use": "Use when you need to make a hole in a wall"
    },
    "pt": {
      "description": "Permite criar furos em superfícies sólidas",
      "when_to_use": "Use quando precisar fazer um furo em uma parede"
    }
  }
}
```

**Beneficios**:
- Mantiene todas las traducciones en un solo archivo
- Facilita la adición de nuevos idiomas
- Asegura coherencia entre versiones

## Consideraciones de Implementación

1. **Compatibilidad Retroactiva**: Todas las extensiones propuestas son campos opcionales que no rompen compatibilidad con la versión actual.

2. **Modelo de Extensión Gradual**: Implementar primero los metadatos y ejemplos, luego avanzar a características más complejas.

3. **Validación Mejorada**: Actualizar el esquema JSON para validar los nuevos campos opcionales.

4. **Documentación Clara**: Proporcionar ejemplos completos de cada extensión.

## Próximos Pasos Recomendados

1. Desarrollar un prototipo con los campos de metadatos y ejemplos
2. Probar con diferentes tipos de herramientas (físicas, digitales, híbridas)
3. Solicitar feedback de la comunidad
4. Implementar la versión 0.2.0 con las extensiones iniciales
5. Planificar la hoja de ruta para características más avanzadas 