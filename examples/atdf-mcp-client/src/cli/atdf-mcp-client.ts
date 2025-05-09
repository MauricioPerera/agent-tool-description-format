#!/usr/bin/env node
/**
 * CLI para el cliente ATDF-MCP
 * 
 * Esta herramienta permite interactuar con servidores MCP
 * y convertir herramientas entre formatos MCP y ATDF.
 */

import { Command } from 'commander';
import * as fs from 'fs-extra';
import * as path from 'path';
import { ATDFMCPClient } from '../client/ATDFMCPClient';

// Crear el programa CLI
const program = new Command();

// Configuración básica
program
  .name('atdf-mcp-client')
  .description('Cliente MCP con soporte para herramientas ATDF')
  .version('1.0.0');

// Comando para descubrir herramientas en un servidor MCP
program
  .command('discover')
  .description('Descubrir herramientas en un servidor MCP y convertirlas a ATDF')
  .argument('<serverUrl>', 'URL del servidor MCP')
  .option('-o, --output <directory>', 'Directorio donde guardar las herramientas ATDF', './atdf-tools')
  .option('-p, --pretty', 'Formatear bonito el JSON guardado', true)
  .option('-w, --when-to-use <text>', 'Texto por defecto para el campo when_to_use')
  .action(async (serverUrl, options) => {
    try {
      // Configurar cliente
      const client = new ATDFMCPClient(serverUrl, undefined, {
        includeWhenToUse: true,
        defaultWhenToUse: options.whenToUse
      });
      
      // Conectar y descubrir herramientas
      console.log(`Conectando al servidor MCP: ${serverUrl}`);
      await client.connect(); // Conectar primero para obtener herramientas MCP
      
      // Obtener herramientas ATDF ya convertidas
      const atdfTools = client.getATDFTools();
      
      // Mostrar herramientas descubiertas
      console.log(`\nHerramientas descubiertas (${atdfTools.length}):`);
      atdfTools.forEach(tool => {
        console.log(`- ${tool.tool_id}: ${tool.description}`);
      });
      
      // Guardar herramientas si se especificó un directorio
      if (options.output) {
        const files = client.saveATDFToolsToDirectory(options.output, options.pretty);
        console.log(`\nHerramientas ATDF guardadas en ${options.output}`);
        console.log(`Total: ${files.length} archivos guardados`);
      }
    } catch (error: any) {
      console.error('Error:', error.message);
      process.exit(1);
    }
  });

// Comando para ejecutar una herramienta ATDF
program
  .command('execute')
  .description('Ejecutar una herramienta ATDF en un servidor MCP')
  .argument('<serverUrl>', 'URL del servidor MCP')
  .argument('<toolId>', 'ID de la herramienta ATDF a ejecutar')
  .option('-p, --params <json>', 'Parámetros para la herramienta en formato JSON', '{}')
  .option('--param <param...>', 'Parámetros individuales en formato clave=valor')
  .action(async (serverUrl, toolId, options) => {
    try {
      // Conectar al servidor
      const client = new ATDFMCPClient(serverUrl);
      await client.connect();
      
      // Preparar parámetros
      let params: any = {};
      
      // Primero cargar del JSON si se proporcionó
      if (options.params && options.params !== '{}') {
        try {
          params = JSON.parse(options.params);
        } catch (e) {
          console.error('Error al parsear JSON de parámetros:', options.params);
          process.exit(1);
        }
      }
      
      // Luego agregar parámetros individuales (sobrescriben los del JSON)
      if (options.param && Array.isArray(options.param)) {
        for (const paramPair of options.param) {
          const [key, value] = paramPair.split('=');
          if (key && value !== undefined) {
            // Intentar convertir a tipo correcto
            if (value === 'true') params[key] = true;
            else if (value === 'false') params[key] = false;
            else if (!isNaN(Number(value))) params[key] = Number(value);
            else params[key] = value;
          }
        }
      }
      
      // Ejecutar la herramienta
      console.log(`Ejecutando herramienta ${toolId} con parámetros:`, params);
      
      const result = await client.executeATDFTool(toolId, params);
      
      // Mostrar resultado
      if (result.status === 'success') {
        console.log('\nResultado exitoso:');
        console.log(JSON.stringify(result.result, null, 2));
      } else {
        console.error('\nError al ejecutar la herramienta:');
        console.error(result.error);
      }
    } catch (error: any) {
      console.error('Error:', error.message);
      process.exit(1);
    }
  });

// Comando para convertir archivos JSON de herramientas MCP a ATDF
program
  .command('convert')
  .description('Convertir herramientas MCP a formato ATDF')
  .argument('<inputFile>', 'Archivo JSON con herramientas MCP o directorio con archivos JSON')
  .option('-o, --output <directory>', 'Directorio donde guardar las herramientas ATDF', './atdf-tools')
  .option('-p, --pretty', 'Formatear bonito el JSON guardado', true)
  .action(async (inputPath, options) => {
    try {
      // Verificar si es un archivo o directorio
      const stats = fs.statSync(inputPath);
      
      if (stats.isFile()) {
        // Convertir un único archivo
        const mcpTool = fs.readJsonSync(inputPath);
        const client = new ATDFMCPClient('http://localhost');
        
        // Convertir la herramienta
        const atdfTool = client.convertToolToATDF(mcpTool);
        
        // Determinar la ruta de salida
        const outputFile = path.join(
          options.output, 
          `${atdfTool.tool_id || path.basename(inputPath)}.json`
        );
        
        // Guardar la herramienta ATDF
        fs.ensureDirSync(options.output);
        fs.writeJsonSync(outputFile, atdfTool, { spaces: options.pretty ? 2 : 0 });
        
        console.log(`Herramienta convertida y guardada en ${outputFile}`);
      } else if (stats.isDirectory()) {
        // Convertir múltiples archivos en un directorio
        const files = fs.readdirSync(inputPath)
          .filter(file => file.endsWith('.json'))
          .map(file => path.join(inputPath, file));
        
        console.log(`Encontrados ${files.length} archivos JSON para convertir`);
        
        // Asegurarse de que el directorio de salida exista
        fs.ensureDirSync(options.output);
        
        // Convertir cada archivo
        const client = new ATDFMCPClient('http://localhost');
        
        let convertedCount = 0;
        for (const file of files) {
          try {
            const mcpTool = fs.readJsonSync(file);
            const atdfTool = client.convertToolToATDF(mcpTool);
            
            const outputFile = path.join(options.output, `${atdfTool.tool_id}.json`);
            fs.writeJsonSync(outputFile, atdfTool, { spaces: options.pretty ? 2 : 0 });
            
            convertedCount++;
          } catch (e) {
            console.error(`Error al convertir ${file}:`, e);
          }
        }
        
        console.log(`Convertidas ${convertedCount} de ${files.length} herramientas a formato ATDF`);
        console.log(`Archivos guardados en ${options.output}`);
      } else {
        console.error(`La ruta proporcionada no es un archivo ni directorio válido: ${inputPath}`);
        process.exit(1);
      }
    } catch (error: any) {
      console.error('Error:', error.message);
      process.exit(1);
    }
  });

// Comandos adicionales se pueden agregar aquí

// Ejecutar el programa CLI
program.parse(process.argv); 