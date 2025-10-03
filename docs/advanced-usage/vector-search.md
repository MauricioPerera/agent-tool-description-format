---
title: Búsqueda Semántica Vectorial con LanceDB
description: Aprende a integrar una base de datos vectorial ligera y embebida con ATDF para hacer búsqueda semántica de herramientas.
---

# Búsqueda Semántica Vectorial con LanceDB

Esta guía muestra cómo usar [LanceDB](https://lancedb.github.io/lancedb/) como una capa de búsqueda semántica sobre una colección de herramientas descritas en formato ATDF.

LanceDB permite hacer búsqueda por similitud vectorial usando embeddings de texto, y es ideal para usar localmente sin necesidad de un servidor externo.

> ℹ️ **Datos de ejemplo**: El repositorio incluye descriptores listos para usar en `examples/output/`. El script `examples/vector_search_example.py` ya apunta a ese directorio mediante `TOOLS_DIR` para crear el índice.

---

## ✨ Beneficios de esta extensión

- **Simplicidad**: Usa una API sencilla y sin necesidad de servidores.
- **Compatibilidad**: No modifica el protocolo ATDF; opera como una capa de consulta.
- **Multilingüe**: Admite búsquedas semánticas en distintos idiomas.
- **Filtrado**: Permite usar metadatos de ATDF (como `language`, `categories`) como filtros.
- **Persistencia**: Los datos se guardan en disco de forma eficiente con formato Arrow.

---

## 🔄 ¿Por qué añadir búsqueda vectorial a ATDF?

Una de las principales ventajas del formato ATDF es que describe herramientas en lenguaje natural y de forma agnóstica a la implementación. Sin embargo, la búsqueda por palabras clave tiene limitaciones:

1. No captura significados similares expresados con palabras diferentes
2. Requiere coincidencias exactas de subcadenas 
3. Funciona peor en escenarios multilingües

La búsqueda vectorial resuelve estos problemas transformando texto en representaciones numéricas (embeddings) que capturan el significado semántico, no solo las palabras específicas.

### Comparación con el sistema actual

| Búsqueda por palabras clave (actual) | Búsqueda vectorial (con LanceDB) |
|--------------------------------------|----------------------------------|
| Solo encuentra coincidencias literales | Encuentra similitud semántica |
| Requiere palabras exactas en cada idioma | Los embeddings multilingües comprenden significados entre idiomas |
| No ordena resultados por relevancia | Los resultados tienen puntuación de similaridad |
| Más rápida para conjuntos pequeños | Más escalable para grandes colecciones de herramientas |
| No requiere dependencias extra | Requiere dependencias de embedding y almacenamiento |

---

## ⚙️ Instalación

```bash
npm install lancedb @huggingface/inference
```

Opcional: crea una cuenta gratuita en [Hugging Face](https://huggingface.co/) para generar embeddings usando `sentence-transformers/all-MiniLM-L6-v2`.

---

## 🔍 Implementación básica

```js
const lancedb = require("lancedb");
const { HfInference } = require("@huggingface/inference");

const hf = new HfInference("hf_your_api_key");

class ATDFVectorStore {
  constructor() {
    this.dbPath = "atdf_vector_db";
    this.tableName = "tools";
    this.db = null;
    this.table = null;
  }

  async initialize() {
    this.db = await lancedb.connect(this.dbPath);
    const tables = await this.db.tableNames();
    if (tables.includes(this.tableName)) {
      this.table = await this.db.openTable(this.tableName);
    }
  }

  async createFromTools(tools) {
    if (!this.db) await this.initialize();

    const data = await Promise.all(tools.map(async (tool) => {
      const text = `${tool.getDescription()} ${tool.getWhenToUse()}`;
      const embedding = await hf.featureExtraction({
        model: "sentence-transformers/all-MiniLM-L6-v2",
        inputs: text
      });

      return {
        id: tool.toolId,
        text,
        embedding,
        language: tool.defaultLanguage || "default",
        categories: tool.categories || [],
        data: JSON.stringify(tool.toJSON())
      };
    }));

    this.table = await this.db.createTable(this.tableName, data);
    return this.table;
  }

  async searchTools(query, options = {}) {
    if (!this.table) await this.initialize();
    const embedding = await hf.featureExtraction({
      model: "sentence-transformers/all-MiniLM-L6-v2",
      inputs: query
    });

    let search = this.table.search(embedding).limit(options.limit || 5);

    if (options.language) {
      search = search.where(`language = '${options.language}'`);
    }
    if (options.category) {
      search = search.where(`categories LIKE '%${options.category}%'`);
    }

    const results = await search.execute();
    return results.map(item => {
      const toolData = JSON.parse(item.data);
      return { ...toolData, score: item.score };
    });
  }

  async addTool(tool) {
    if (!this.table) await this.initialize();

    const text = `${tool.getDescription()} ${tool.getWhenToUse()}`;
    const embedding = await hf.featureExtraction({
      model: "sentence-transformers/all-MiniLM-L6-v2",
      inputs: text
    });

    await this.table.add([{
      id: tool.toolId,
      text,
      embedding,
      language: tool.defaultLanguage || "default",
      categories: tool.categories || [],
      data: JSON.stringify(tool.toJSON())
    }]);
  }
}
```

---

## 📚 Integración con el SDK de JavaScript

El SDK de JavaScript para ATDF incluye soporte opcional para búsqueda vectorial. Aquí te mostramos cómo usarlo:

### Instalación de dependencias

```bash
# Primero instala el SDK de ATDF
npm install atdf-js

# Luego instala las dependencias opcionales para búsqueda vectorial
npm install lancedb @xenova/transformers
```

### Uso básico

```javascript
const { ATDFToolbox, ATDFVectorStore } = require('atdf-js');

async function main() {
  // 1. Crear e inicializar el almacén vectorial
  const vectorStore = new ATDFVectorStore();
  await vectorStore.initialize();
  
  // 2. Crear un Toolbox con el almacén vectorial
  const toolbox = new ATDFToolbox({ vectorStore });
  
  // 3. Cargar herramientas desde un directorio
  toolbox.loadToolsFromDirectory('./tools');
  
  // 4. Realizar una búsqueda vectorial
  const results = await toolbox.searchTools('enviar un mensaje', { 
    useVectorSearch: true,  // Activar búsqueda vectorial
    language: 'es'          // Opcional: filtrar por idioma
  });
  
  console.log(results);
}

main().catch(console.error);
```

### Comparación de resultados

Una forma visual de ver la diferencia entre ambos métodos de búsqueda:

```javascript
async function compareBothSearches(query) {
  console.log(`Comparando búsquedas para: "${query}"\n`);
  
  // Búsqueda estándar (palabras clave)
  console.log('Resultados con búsqueda por palabras clave:');
  const standardResults = await toolbox.searchTools(query);
  standardResults.forEach((tool, i) => {
    console.log(`${i+1}. ${tool.toolId} - ${tool.getDescription()}`);
  });
  
  console.log('\nResultados con búsqueda vectorial:');
  const vectorResults = await toolbox.searchTools(query, { useVectorSearch: true });
  vectorResults.forEach((tool, i) => {
    console.log(`${i+1}. ${tool.toolId} - ${tool.getDescription()}`);
  });
}

// Ejemplo de consulta ambigua o semántica
compareBothSearches('comunicarme con alguien');
```

### Implementación detallada

La clase `ATDFVectorStore` en el SDK proporciona estas funcionalidades principales:

- **Verificación de dependencias**: Comprueba si las bibliotecas opcionales están instaladas
- **Inicialización bajo demanda**: Crea o conecta a la BD vectorial solo cuando es necesario
- **Detección de idioma**: Usa metadatos de idioma para búsquedas y filtros precisos
- **Fallback automático**: Si hay un error con la búsqueda vectorial, usa la búsqueda estándar

---

## 🔄 Integración con agentes LLM

Puedes usar esta capa como filtro previo antes de invocar el agente. Por ejemplo:

```javascript
// 1. Obtener herramientas relevantes basadas en la intención del usuario
const relevantTools = await toolbox.searchTools(userPrompt, { 
  useVectorSearch: true,
  limit: 5 
});

// 2. Convertir a formato compatible con un agente LangChain/AutoGPT/etc.
const toolDescriptions = relevantTools.map(tool => ({
  name: tool.toolId,
  description: tool.getDescription(),
  parameters: tool.getInputSchema()
}));

// 3. Configurar el agente con solo las herramientas relevantes
agent.setTools(toolDescriptions);

// 4. Ejecutar el agente con estas herramientas limitadas
const result = await agent.run(userPrompt);
```

Esto produce varios beneficios:

1. **Mejor selección**: El agente recibe solo herramientas relevantes al contexto
2. **Menos tokens**: Reduces el consumo de tokens al enviar menos herramientas al LLM
3. **Mayor precisión**: Reduces las posibilidades de que el LLM seleccione herramientas incorrectas

---

## 🌐 Soluciones alternativas

### SQLite + sqlite-vss

SQLite con la extensión VSS ofrece capacidades vectoriales con una base de datos relacional familiar:

```javascript
const Database = require('better-sqlite3');
const db = new Database('atdf_tools.db');

// Cargar la extensión VSS
db.loadExtension('sqlite-vss');

// Crear tabla y índice vectorial
db.exec(`
  CREATE TABLE tools(id TEXT PRIMARY KEY, data JSON, embedding BLOB);
  CREATE VIRTUAL TABLE tools_vss USING vss0(embedding(384));
  CREATE TRIGGER tools_vss_insert AFTER INSERT ON tools
    BEGIN
      INSERT INTO tools_vss(rowid, embedding) VALUES (new.rowid, new.embedding);
    END;
`);
```

### vectordb (Solución 100% JavaScript)

Si prefieres evitar dependencias nativas, `vectordb` es una opción ligera:

```javascript
const { VectorDB } = require('vectordb');

// Crear base de datos en memoria (o en disco)
const db = new VectorDB();

// Insertar herramientas
tools.forEach(tool => {
  db.insert({
    id: tool.toolId,
    vector: toolEmbedding,  // Genera este embedding con otra librería
    payload: tool.toJSON()
  });
});

// Búsqueda
const results = db.search({
  vector: queryEmbedding,
  k: 5,
  includeVectors: false,
  includePayloads: true
});
```

### hnswlib-node (Alto rendimiento)

Para colecciones muy grandes, `hnswlib-node` ofrece mejor rendimiento:

```javascript
const hnswlib = require('hnswlib-node');
const fs = require('fs');

// Crear índice
const dimension = 384;  // Dimensión de tus embeddings
const maxElements = 10000;
const index = new hnswlib.HierarchicalNSW('cosine', dimension);
index.initIndex(maxElements);

// Mapeo de IDs numéricos a objetos tool
const toolMap = {};
tools.forEach((tool, i) => {
  index.addPoint(toolEmbedding, i);
  toolMap[i] = tool;
});

// Búsqueda
const results = index.searchKnn(queryEmbedding, 5);
const matchedTools = results.neighbors.map(id => toolMap[id]);

// Persistencia
index.writeIndex('tools_index.bin');
fs.writeFileSync('tools_map.json', JSON.stringify(toolMap));
```

---

## 🚀 Rendimiento y consideraciones

### Memoria y almacenamiento

- LanceDB almacena los datos de forma eficiente usando formato Arrow
- Para ~1000 herramientas, el tamaño de la base de datos es de aproximadamente 10-20MB
- Durante la búsqueda, el uso de memoria depende del modelo de embeddings (100MB-1GB)

### Velocidad

- Generación de embeddings: ~50-200ms por herramienta (depende del servicio o modelo local)
- Búsqueda vectorial: 5-20ms para colecciones de hasta 10,000 herramientas
- Primera inicialización: 1-3s (carga del modelo de embeddings)

### Caché de embeddings

Si usas un servicio externo para embeddings, considera implementar caché:

```javascript
async function getCachedEmbedding(text, cacheDir = ".embeddings_cache") {
  const hash = crypto.createHash('md5').update(text).digest('hex');
  const cachePath = path.join(cacheDir, `${hash}.json`);
  
  if (fs.existsSync(cachePath)) {
    return JSON.parse(fs.readFileSync(cachePath, 'utf8'));
  }
  
  const embedding = await getEmbedding(text);
  
  // Guardar en caché
  if (!fs.existsSync(cacheDir)) {
    fs.mkdirSync(cacheDir, { recursive: true });
  }
  fs.writeFileSync(cachePath, JSON.stringify(embedding));
  
  return embedding;
}
```

---

## 📊 Conclusión

Esta extensión opcional mejora el protocolo ATDF con una capa de búsqueda semántica, sin modificar su estructura fundamental. La naturaleza embebida de LanceDB lo hace ideal para aplicaciones que necesitan búsqueda avanzada sin infraestructura adicional.

Puedes usar esta estrategia en apps de escritorio, CLIs, herramientas locales, o incluso en backends ligeros que consumen colecciones ATDF. 