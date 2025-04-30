/**
 * Ejemplo de uso de búsqueda vectorial con ATDF
 * 
 * NOTA: Para ejecutar este ejemplo, primero debes instalar las dependencias opcionales:
 * npm install lancedb @xenova/transformers
 * 
 * Uso:
 * node examples/vector_search.js
 */

const { ATDFToolbox, ATDFVectorStore } = require('../src');
const path = require('path');

// Función principal
async function demoVectorSearch() {
  console.log('=== DEMOSTRACIÓN DE BÚSQUEDA VECTORIAL CON ATDF ===\n');
  
  // Verificar dependencias
  try {
    require('lancedb');
    require('@xenova/transformers');
  } catch (error) {
    console.error('❌ Error: Dependencias no instaladas');
    console.error('Para usar búsqueda vectorial, instala las dependencias opcionales:');
    console.error('npm install lancedb @xenova/transformers');
    process.exit(1);
  }
  
  try {
    // 1. Crear un almacén vectorial
    console.log('1️⃣ Creando e inicializando almacén vectorial...');
    const vectorStore = new ATDFVectorStore({
      dbPath: path.join(__dirname, 'atdf_vector_db'),
      tableName: 'demo_tools'
    });
    
    // 2. Inicializar el almacén
    console.log('   Inicializando almacén vectorial...');
    await vectorStore.initialize();
    console.log('   ✅ Almacén vectorial inicializado');
    
    // 3. Crear un toolbox con el almacén vectorial
    console.log('\n2️⃣ Creando toolbox con soporte vectorial...');
    const toolbox = new ATDFToolbox({ vectorStore });
    
    // 4. Cargar herramientas desde un directorio
    const toolsPath = path.join(__dirname, '../../schema/examples');
    console.log(`\n3️⃣ Cargando herramientas desde ${toolsPath}...`);
    
    const loadedCount = toolbox.loadToolsFromDirectory(toolsPath, true);
    console.log(`   ✅ Cargadas ${loadedCount} herramientas`);
    console.log(`   ℹ️ Esperando indexación de herramientas en la BD vectorial...`);
    
    // Dar tiempo a que se completen las operaciones asíncronas
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // 5. Realizar búsquedas de prueba
    await runSearchTests(toolbox);
    
    // 6. Ejemplo de comparación
    await runComparisonExample(toolbox);
    
  } catch (error) {
    console.error('❌ Error en la demostración:', error);
  }
}

// Realiza varias búsquedas de prueba
async function runSearchTests(toolbox) {
  console.log('\n4️⃣ Realizando búsquedas de prueba:\n');
  
  const queries = [
    'enviar mensaje',
    'almacenar archivos',
    'análisis de datos',
    'navegar en el mapa',
    'procesamiento de imágenes'
  ];
  
  for (const query of queries) {
    console.log(`\n📝 CONSULTA: "${query}"`);
    
    // Búsqueda estándar
    console.log(' 🔍 Resultados con búsqueda estándar:');
    const standardResults = await toolbox.searchTools(query);
    if (standardResults.length === 0) {
      console.log('   - No se encontraron resultados');
    } else {
      standardResults.slice(0, 3).forEach((tool, i) => {
        console.log(`   ${i+1}. ${tool.toolId} - ${tool.getDescription()}`);
      });
      if (standardResults.length > 3) {
        console.log(`   ... y ${standardResults.length - 3} más`);
      }
    }
    
    // Búsqueda vectorial
    console.log(' 🧠 Resultados con búsqueda vectorial:');
    try {
      const vectorResults = await toolbox.searchTools(query, { useVectorSearch: true });
      if (vectorResults.length === 0) {
        console.log('   - No se encontraron resultados');
      } else {
        vectorResults.slice(0, 3).forEach((tool, i) => {
          console.log(`   ${i+1}. ${tool.toolId} - ${tool.getDescription()}`);
        });
        if (vectorResults.length > 3) {
          console.log(`   ... y ${vectorResults.length - 3} más`);
        }
      }
    } catch (error) {
      console.error('   ❌ Error en búsqueda vectorial:', error.message);
    }
    
    console.log('---------------------------------------------------');
  }
}

// Ejemplo de comparación de ambos métodos con consulta semántica
async function runComparisonExample(toolbox) {
  console.log('\n5️⃣ COMPARACIÓN EN PROFUNDIDAD: BÚSQUEDA SEMÁNTICA\n');
  
  // Consulta semántica (no coincide exactamente con palabras clave)
  const semanticQuery = 'comunicarse con alguien';
  console.log(`📝 Consulta semántica: "${semanticQuery}"`);
  console.log('   Esta consulta no contiene palabras clave exactas de ninguna herramienta.');
  
  // Búsqueda estándar
  console.log('\n🔍 Resultados con búsqueda por palabras clave:');
  const standardResults = await toolbox.searchTools(semanticQuery);
  
  if (standardResults.length === 0) {
    console.log('   - La búsqueda por palabras clave no encontró coincidencias');
  } else {
    standardResults.forEach((tool, i) => {
      console.log(`   ${i+1}. ${tool.toolId} - ${tool.getDescription()}`);
    });
  }
  
  // Búsqueda vectorial 
  console.log('\n🧠 Resultados con búsqueda vectorial (semántica):');
  try {
    const vectorResults = await toolbox.searchTools(semanticQuery, { useVectorSearch: true });
    
    if (vectorResults.length === 0) {
      console.log('   - La búsqueda vectorial no encontró coincidencias');
    } else {
      vectorResults.forEach((tool, i) => {
        console.log(`   ${i+1}. ${tool.toolId} - ${tool.getDescription()}`);
        // Mostrar más detalles para el primer resultado
        if (i === 0) {
          console.log(`      → Esta herramienta fue detectada por similitud semántica`);
          console.log(`      → Ejemplo de uso: ${tool.getWhenToUse()}`);
        }
      });
    }
  } catch (error) {
    console.error('   ❌ Error en búsqueda vectorial:', error.message);
  }
  
  console.log('\n✨ CONCLUSIÓN:');
  console.log(' • La búsqueda vectorial puede encontrar herramientas semánticamente');
  console.log('   relacionadas incluso cuando no hay coincidencia exacta de palabras.');
  console.log(' • Esto es especialmente útil para consultas ambiguas o cuando');
  console.log('   los usuarios no conocen las palabras exactas para describir la herramienta.');
  console.log(' • En contextos multilingües, la búsqueda vectorial puede encontrar');
  console.log('   herramientas relevantes incluso si la consulta está en otro idioma.');
  
  console.log('\n=== DEMOSTRACIÓN COMPLETADA ===');
}

// Ejecutar la demostración
demoVectorSearch().catch(err => {
  console.error('Error grave en la demostración:', err);
}); 