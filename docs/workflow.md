# ATDF Workflow

[Home](index.md) | [Specification](specification.md) | [Examples](examples.md) | [Contributing](contributing.md) | [Multilingual](multilingual.md) | [Workflow](workflow.md) | [Changelog](changelog.md) | [License](license.md)

This page illustrates how ATDF works in practice with Mermaid diagrams.

## Basic ATDF Flow

```mermaid
graph TD
    A[User Request] -->|"e.g., 'Make a hole in the wall'"| B[AI Agent]
    B -->|Load| C[ATDF Tool Descriptions]
    C -->|Select Tool| D[hole_maker_v1]
    D -->|Execute| E[Task Completed]
    
    subgraph Tool Selection Process
    F[Parse User Intent] -->|Match with| G["when_to_use Field"]
    G -->|Find| H[Appropriate Tool]
    H -->|Extract| I[Required Inputs]
    end
```

## Multilingual Tool Selection

```mermaid
graph TD
    A[User Request] -->|In Any Language| B[AI Agent]
    B -->|Detect Language| C{Language?}
    C -->|English| D[English Tools]
    C -->|Spanish| E[Spanish Tools]
    C -->|Portuguese| F[Portuguese Tools]
    
    D -->|Select| G[Execute Tool]
    E -->|Select| G
    F -->|Select| G
```

## Tool Validation Process

```mermaid
graph TD
    A[Create Tool Description] -->|JSON Format| B[Validation]
    B -->|JSON Schema| C{Valid?}
    C -->|Yes| D[Add to Tool Repository]
    C -->|No| E[Fix Issues]
    E --> B
```

## ATDF in Agent Ecosystem

```mermaid
graph TD
    A[AI Agent] -->|Uses| B[ATDF Protocol]
    B -->|Loads| C[Tool Descriptions]
    
    subgraph Physical Tools
    D[hole_maker]
    E[paint_brush]
    end
    
    subgraph Digital Tools
    F[text_translator]
    G[image_processor]
    end
    
    C --- D
    C --- E
    C --- F
    C --- G
    
    H[User Request] -->|Prompt| A
    A -->|Selects Tool| I[Executes Action]
```

## Cross-Language Interoperability

```mermaid
graph TD
    A["User Query (Español): 'hacer un agujero'"] -->|Language Detection| B["Detected: Spanish"]
    B -->|Tool Selection| C["Tools with es Language"]
    
    D["User Query (English): 'make a hole'"] -->|Language Detection| E["Detected: English"]
    E -->|Tool Selection| F["Tools with en Language"]
    
    G["User Query (Português): 'fazer um furo'"] -->|Language Detection| H["Detected: Portuguese"]
    H -->|Tool Selection| I["Tools with pt Language"]
    
    C -->|Select| J["hole_maker_v1 (es)"]
    F -->|Select| K["hole_maker_v1 (en)"]
    I -->|Select| L["hole_maker_v1 (pt)"]
    
    J -->|Same Functionality| M["Functional Equivalence"]
    K -->|Same Functionality| M
    L -->|Same Functionality| M
``` 