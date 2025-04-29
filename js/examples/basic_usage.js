/**
 * Ejemplo básico de uso del SDK de ATDF en JavaScript
 */
const path = require('path');
const { 
  loadToolboxFromDirectory, 
  findBestTool,
  ATDFTool 
} = require('../src');

// Función para separador visual
function printSeparator(title) {
  console.log('\n' + '='.repeat(50));
  if (title) console.log(title);
  console.log('='.repeat(50));
}

// Ejemplo 1: Cargar herramientas desde un directorio
function ejemploCargarHerramientas() {
  printSeparator('EJEMPLO: CARGAR HERRAMIENTAS');
  
  // Ruta a los ejemplos (ajusta según sea necesario)
  const examplesPath = path.resolve(__dirname, '../../schema/examples');
  
  console.log(`Cargando herramientas desde: ${examplesPath}`);
  const toolbox = loadToolboxFromDirectory(examplesPath, { recursive: true });
  
  console.log(`Se cargaron ${toolbox.size} herramientas`);
  
  // Mostrar las herramientas cargadas
  console.log('\nHerramientas disponibles:');
  toolbox.tools.forEach(tool => {
    console.log(`- ${tool.toolId}: ${tool.getDescription()}`);
  });
  
  return toolbox;
}

// Ejemplo 2: Buscar herramientas
function ejemploBuscarHerramientas(toolbox) {
  printSeparator('EJEMPLO: BUSCAR HERRAMIENTAS');
  
  // Buscar por texto
  const searchText = 'perforación';
  console.log(`Buscando herramientas relacionadas con "${searchText}":`);
  
  const results = toolbox.searchTools(searchText);
  
  if (results.length > 0) {
    results.forEach(tool => {
      console.log(`- ${tool.toolId}: ${tool.getDescription()}`);
    });
  } else {
    console.log('No se encontraron herramientas que coincidan con la búsqueda.');
  }
  
  // Buscar en otro idioma
  const searchTextEn = 'hole';
  console.log(`\nBuscando herramientas en inglés relacionadas con "${searchTextEn}":`);
  
  const resultsEn = toolbox.searchTools(searchTextEn, { language: 'en' });
  
  if (resultsEn.length > 0) {
    resultsEn.forEach(tool => {
      console.log(`- ${tool.toolId}: ${tool.getDescription('en')}`);
    });
  } else {
    console.log('No se encontraron herramientas que coincidan con la búsqueda en inglés.');
  }
}

// Ejemplo 3: Selección automática de herramientas
function ejemploSeleccionAutomatica(toolbox) {
  printSeparator('EJEMPLO: SELECCIÓN AUTOMÁTICA DE HERRAMIENTAS');
  
  // Escenario en español
  const objetivo = 'Necesito hacer un agujero en la pared';
  console.log(`Objetivo: "${objetivo}"`);
  
  const herramientaSeleccionada = findBestTool(toolbox, objetivo);
  
  if (herramientaSeleccionada) {
    console.log('\nHerramienta seleccionada:');
    console.log(`- ID: ${herramientaSeleccionada.toolId}`);
    console.log(`- Descripción: ${herramientaSeleccionada.getDescription()}`);
    console.log(`- Cuándo usar: ${herramientaSeleccionada.getWhenToUse()}`);
  } else {
    console.log('\nNo se encontró una herramienta adecuada para el objetivo.');
  }
  
  // Escenario en inglés
  const goal = 'I need to translate some text from Spanish to English';
  console.log(`\nGoal: "${goal}"`);
  
  const selectedTool = findBestTool(toolbox, goal, { language: 'en' });
  
  if (selectedTool) {
    console.log('\nSelected tool:');
    console.log(`- ID: ${selectedTool.toolId}`);
    console.log(`- Description: ${selectedTool.getDescription('en')}`);
    console.log(`- When to use: ${selectedTool.getWhenToUse('en')}`);
  } else {
    console.log('\nNo suitable tool found for the goal.');
  }
}

// Ejemplo 4: Crear una herramienta desde código
function ejemploCrearHerramienta() {
  printSeparator('EJEMPLO: CREAR HERRAMIENTA DESDE CÓDIGO');
  
  const toolData = {
    tool_id: 'custom_calculator_v1',
    description: 'Realiza operaciones matemáticas básicas',
    when_to_use: 'Cuando necesites realizar cálculos matemáticos simples',
    how_to_use: {
      inputs: [
        { name: 'operation', type: 'string', description: 'Operación a realizar (suma, resta, multiplicación, división)' },
        { name: 'operand1', type: 'number', description: 'Primer operando' },
        { name: 'operand2', type: 'number', description: 'Segundo operando' }
      ],
      outputs: {
        success: 'Cálculo realizado correctamente',
        failure: [
          { code: 'invalid_operation', description: 'La operación especificada no es válida' },
          { code: 'division_by_zero', description: 'No se puede dividir por cero' }
        ]
      }
    }
  };
  
  const calculator = new ATDFTool(toolData);
  console.log('Herramienta creada:');
  console.log(`- ID: ${calculator.toolId}`);
  console.log(`- Descripción: ${calculator.getDescription()}`);
  console.log(`- Entradas requeridas: ${calculator.inputs.length}`);
  
  // Mostrar schema de validación
  console.log('\nEsquema de validación generado:');
  console.log(JSON.stringify(calculator.getInputSchema(), null, 2));
}

// Ejemplo 5: Escenario completo
function ejemploCompleto(toolbox) {
  printSeparator('EJEMPLO COMPLETO: ESCENARIO DE USO REAL');
  
  // 1. Recibir una petición del usuario
  const peticionUsuario = 'Necesito hacer un agujero en la pared para colgar un cuadro';
  console.log(`Petición del usuario: "${peticionUsuario}"`);
  
  // 2. Detectar el idioma (simulado)
  const idiomaDetectado = 'es';
  console.log(`Idioma detectado: ${idiomaDetectado}`);
  
  // 3. Encontrar la herramienta más adecuada
  console.log('\nBuscando la herramienta más adecuada...');
  const herramienta = findBestTool(toolbox, peticionUsuario, { language: idiomaDetectado });
  
  if (!herramienta) {
    console.log('No se encontró una herramienta adecuada para esta tarea.');
    return;
  }
  
  // 4. Mostrar información de la herramienta
  console.log(`\nHerramienta seleccionada: ${herramienta.toolId}`);
  console.log(`Descripción: ${herramienta.getDescription(idiomaDetectado)}`);
  console.log(`Cuándo usar: ${herramienta.getWhenToUse(idiomaDetectado)}`);
  
  // 5. Verificar prerrequisitos
  console.log('\nVerificando prerrequisitos...');
  if (herramienta.prerequisites) {
    Object.entries(herramienta.prerequisites).forEach(([categoria, items]) => {
      console.log(`- ${categoria}:`);
      items.forEach(item => console.log(`  * ${item}`));
    });
  } else {
    console.log('No hay prerrequisitos especificados para esta herramienta.');
  }
  
  // 6. Recopilar entradas del usuario (simulado)
  console.log('\nRecopilando entradas necesarias:');
  const entradas = {};
  
  herramienta.inputs.forEach(input => {
    console.log(`- ${input.name} (${input.type}): ${input.description}`);
    
    // Simular valores proporcionados por el usuario
    if (input.name === 'location') {
      entradas[input.name] = 'x:50,y:120';
    } else if (input.name === 'bit_id' || input.name === 'surface_type') {
      entradas[input.name] = 'pared_yeso';
    } else if (input.name === 'configuration') {
      entradas[input.name] = {
        depth: 30,
        diameter: 8
      };
    }
    
    console.log(`  Valor proporcionado: ${JSON.stringify(entradas[input.name])}`);
  });
  
  // 7. Ejecutar la herramienta (simulado)
  console.log('\nEjecutando la herramienta...');
  console.log(`Resultado: ${herramienta.successMessage}`);
}

// Ejecutar todos los ejemplos
function main() {
  console.log('EJEMPLOS DE USO DEL SDK DE ATDF EN JAVASCRIPT\n');
  
  // Cargar herramientas (compartidas entre ejemplos)
  const toolbox = ejemploCargarHerramientas();
  
  // Ejecutar ejemplos individuales
  ejemploBuscarHerramientas(toolbox);
  ejemploSeleccionAutomatica(toolbox);
  ejemploCrearHerramienta();
  
  // Ejecutar el ejemplo completo
  ejemploCompleto(toolbox);
  
  console.log('\n¡Todos los ejemplos se han ejecutado correctamente!');
}

// Ejecutar el programa principal
main(); 