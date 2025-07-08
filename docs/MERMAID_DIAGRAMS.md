# 📊 Diagramas Mermaid ATDF

Este archivo contiene todos los diagramas Mermaid utilizados en la documentación ATDF, optimizados para máxima legibilidad y compilación correcta.

## 🔄 Flujo de Trabajo ATDF

### 1. Descripción de Herramientas
```mermaid
flowchart LR
    A[Desarrollador] --> B[Copia Plantilla ATDF]
    B --> C[Completa Campos Requeridos]
    C --> D[Define Esquema de Entrada]
    D --> E[Agrega Metadatos Opcionales]
    E --> F[Agente de IA Consume]
    
    style A fill:#e1f5fe
    style F fill:#f3e5f5
    style B fill:#fff3e0
    style C fill:#fff3e0
    style D fill:#fff3e0
    style E fill:#fff3e0
```

### 2. Manejo de Errores
```mermaid
flowchart LR
    A[Error Ocurre] --> B[Copia Plantilla de Error]
    B --> C[Llena Campos Requeridos]
    C --> D[Agrega Contexto Opcional]
    D --> E[Agente Recibe Error]
    E --> F[Corrección Automática]
    
    style A fill:#ffebee
    style F fill:#e8f5e8
    style B fill:#fff3e0
    style C fill:#fff3e0
    style D fill:#fff3e0
    style E fill:#fff3e0
```

## 🔍 Proceso de Descubrimiento

### Descubrimiento de Herramientas
```mermaid
flowchart LR
    A[Agente de IA] --> B[GET /tools]
    B --> C[Descripción de Herramientas]
    C --> D[Esquemas de Entrada]
    
    style A fill:#e3f2fd
    style B fill:#fff3e0
    style C fill:#e8f5e8
    style D fill:#f3e5f5
```

### Ejecución de Herramientas
```mermaid
flowchart LR
    A[Agente] --> B[POST /api/tool/execute]
    B --> C[Validación de Entrada]
    C --> D[Lógica de Negocio]
    D --> E[Respuesta]
    
    style A fill:#e3f2fd
    style B fill:#fff3e0
    style C fill:#e8f5e8
    style D fill:#fff3e0
    style E fill:#f3e5f5
```

### Manejo de Errores
```mermaid
flowchart LR
    A[Error Ocurre] --> B[Formato ATDF]
    B --> C[Contexto Enriquecido]
    C --> D[Corrección Automática]
    D --> E[Reintento]
    
    style A fill:#ffebee
    style B fill:#fff3e0
    style C fill:#e8f5e8
    style D fill:#e3f2fd
    style E fill:#f3e5f5
```

## 🚀 Flujo Completo de Trabajo

### Proceso End-to-End
```mermaid
flowchart TD
    A[Desarrollador] --> B[Copia Plantilla ATDF]
    B --> C[Completa Campos Requeridos]
    C --> D[Define Esquema de Entrada]
    D --> E[Implementa Lógica]
    E --> F[Agente de IA Descubre]
    F --> G[Agente Ejecuta Herramienta]
    G --> H{¿Éxito?}
    H -->|Sí| I[Respuesta de Éxito]
    H -->|No| J[Respuesta de Error ATDF]
    J --> K[Agente Corrige Automáticamente]
    K --> G
    
    style A fill:#e1f5fe
    style F fill:#e3f2fd
    style I fill:#e8f5e8
    style J fill:#ffebee
    style K fill:#fff3e0
```

## ⚖️ Comparación: Sin ATDF vs Con ATDF

### Flujo de Errores
```mermaid
flowchart LR
    subgraph "Sin ATDF"
        A1[Error Genérico] --> B1[Agente Confundido]
        B1 --> C1[Reintentos Aleatorios]
        C1 --> D1[Fallo]
    end
    
    subgraph "Con ATDF"
        A2[Error Enriquecido] --> B2[Contexto Claro]
        B2 --> C2[Valor Sugerido]
        C2 --> D2[Corrección Automática]
        D2 --> E2[Éxito]
    end
    
    style A1 fill:#ffebee
    style D1 fill:#ffebee
    style A2 fill:#fff3e0
    style E2 fill:#e8f5e8
```

## 🏗️ Arquitectura ATDF

### Componentes del Sistema
```mermaid
flowchart TD
    A[Tool Registry] --> B[Tool Descriptions]
    C[Error Handler] --> D[ATDF Error Format]
    E[Validator] --> F[Input Validation]
    G[Agent] --> H[Tool Discovery]
    H --> I[Tool Execution]
    I --> J[Success Response]
    I --> K[Error Response]
    K --> L[Auto Correction]
    L --> I
    
    style A fill:#e1f5fe
    style C fill:#ffebee
    style E fill:#fff3e0
    style G fill:#e3f2fd
    style J fill:#e8f5e8
    style K fill:#ffebee
    style L fill:#fff3e0
```

## 🎯 Tipos de Herramientas

### Categorías de Herramientas
```mermaid
mindmap
  root((ATDF Tools))
    Información
      Búsqueda Web
      Consulta BD
      Análisis Datos
      Reportes
    Acción
      CRUD Registros
      Envío Emails
      Procesar Pagos
      Programar Tareas
    Validación
      Verificar Datos
      Validar Documentos
      Comprobar Permisos
      Analizar Contenido
    Transformación
      Convertir Formatos
      Procesar Imágenes
      Traducir Texto
      Generar Código
```

## 🔄 Ciclo de Vida de Herramienta

### Fases de Desarrollo
```mermaid
flowchart LR
    A[Diseño] --> B[Implementación]
    B --> C[Testing]
    C --> D[Despliegue]
    D --> E[Monitoreo]
    E --> F[Mantenimiento]
    F --> A
    
    style A fill:#e1f5fe
    style B fill:#fff3e0
    style C fill:#e8f5e8
    style D fill:#e3f2fd
    style E fill:#f3e5f5
    style F fill:#fff3e0
```

## 🎨 Paleta de Colores

Los diagramas utilizan una paleta de colores consistente:

- **Azul Claro** (`#e1f5fe`): Inicio/Desarrollador
- **Azul Medio** (`#e3f2fd`): Agente de IA
- **Naranja** (`#fff3e0`): Procesos/Validación
- **Verde** (`#e8f5e8`): Éxito/Validación
- **Rojo Claro** (`#ffebee`): Errores
- **Púrpura** (`#f3e5f5`): Resultados/Metadatos

## 📝 Notas de Implementación

### Sintaxis Mermaid Utilizada

1. **flowchart**: Para diagramas de flujo
2. **mindmap**: Para mapas mentales
3. **style**: Para colorear nodos
4. **subgraph**: Para agrupar elementos
5. **flowchart TD**: Para flujos top-down
6. **flowchart LR**: Para flujos left-right

### Mejores Prácticas

- ✅ Usar `flowchart` en lugar de `graph` (más moderno)
- ✅ Agregar estilos de color para mejor legibilidad
- ✅ Usar subgraphs para agrupar conceptos relacionados
- ✅ Mantener diagramas simples y enfocados
- ✅ Usar colores consistentes en toda la documentación

---

**Nota**: Estos diagramas están optimizados para renderizarse correctamente en GitHub, GitLab, y otras plataformas que soporten Mermaid. 