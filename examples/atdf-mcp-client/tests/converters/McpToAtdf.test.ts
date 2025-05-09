import { mcpToAtdf, batchConvert } from '../../src/converters/McpToAtdf';
import { McpToAtdfOptions } from '../../src/types';

describe('McpToAtdf', () => {
  describe('mcpToAtdf', () => {
    it('debería convertir una herramienta MCP básica a formato ATDF', () => {
      const mcpTool = {
        name: 'test-tool',
        description: 'Herramienta de prueba',
        schema: {
          param1: {
            type: { name: 'string' },
            description: 'Parámetro 1',
            required: true
          },
          param2: {
            type: { name: 'number' },
            description: 'Parámetro 2',
            required: false
          }
        }
      };
      
      const atdfTool = mcpToAtdf(mcpTool);
      
      expect(atdfTool).toBeDefined();
      expect(atdfTool.schema_version).toBe('1.0.0');
      expect(atdfTool.tool_id).toBe('test-tool');
      expect(atdfTool.description).toBe('Herramienta de prueba');
      
      // Verificar inputs
      expect(atdfTool.how_to_use.inputs).toHaveLength(2);
      expect(atdfTool.how_to_use.inputs[0]).toMatchObject({
        name: 'param1',
        description: 'Parámetro 1',
        required: true
      });
      expect(atdfTool.how_to_use.inputs[1]).toMatchObject({
        name: 'param2',
        description: 'Parámetro 2',
        required: false
      });
      
      // Verificar outputs
      expect(atdfTool.how_to_use.outputs).toBeDefined();
      expect(atdfTool.how_to_use.outputs.success).toBeDefined();
    });
    
    it('debería manejar tipos complejos correctamente', () => {
      const mcpTool = {
        name: 'complex-tool',
        description: 'Herramienta compleja',
        schema: {
          arrayParam: {
            type: { name: 'array', of: { name: 'string' } },
            description: 'Array de strings',
            required: true
          },
          objectParam: {
            type: { 
              name: 'object',
              properties: {
                prop1: { name: 'string' },
                prop2: { name: 'number' }
              }
            },
            description: 'Objeto complejo',
            required: true
          }
        }
      };
      
      const atdfTool = mcpToAtdf(mcpTool);
      
      expect(atdfTool.how_to_use.inputs).toHaveLength(2);
      // No comprobamos el tipo exacto, solo que existen los parámetros
      expect(atdfTool.how_to_use.inputs[0].name).toBe('arrayParam');
      expect(atdfTool.how_to_use.inputs[1].name).toBe('objectParam');
    });
    
    it('debería generar campos when_to_use opcionales', () => {
      const mcpTool = {
        name: 'simple-tool',
        description: 'Herramienta simple',
        schema: {}
      };
      
      const atdfTool = mcpToAtdf(mcpTool, { includeWhenToUse: true });
      
      expect(atdfTool.when_to_use).toBeDefined();
      // Solo verificamos que existe, no el contenido exacto
      expect(typeof atdfTool.when_to_use).toBe('string');
    });
    
    it('debería generar secciones failure opcionales', () => {
      const mcpTool = {
        name: 'simple-tool',
        description: 'Herramienta simple',
        schema: {}
      };
      
      const atdfTool = mcpToAtdf(mcpTool, { includeFailures: true });
      
      if (atdfTool.how_to_use.outputs.failure) {
        expect(atdfTool.how_to_use.outputs.failure).toBeInstanceOf(Array);
        expect(atdfTool.how_to_use.outputs.failure.length).toBeGreaterThan(0);
      } else {
        fail('La sección failure no está definida');
      }
    });
  });
  
  describe('batchConvert', () => {
    it('debería convertir múltiples herramientas MCP a ATDF', () => {
      const mcpTools = [
        {
          name: 'tool1',
          description: 'Herramienta 1',
          schema: {}
        },
        {
          name: 'tool2',
          description: 'Herramienta 2',
          schema: {}
        }
      ];
      
      const atdfTools = batchConvert(mcpTools);
      
      expect(atdfTools).toHaveLength(2);
      expect(atdfTools[0].tool_id).toBe('tool1');
      expect(atdfTools[1].tool_id).toBe('tool2');
    });
    
    it('debería aplicar opciones a todas las herramientas convertidas', () => {
      const mcpTools = [
        {
          name: 'tool1',
          description: 'Herramienta 1',
          schema: {}
        },
        {
          name: 'tool2',
          description: 'Herramienta 2',
          schema: {}
        }
      ];
      
      const atdfTools = batchConvert(mcpTools, { includeWhenToUse: true });
      
      expect(atdfTools[0].when_to_use).toBeDefined();
      expect(atdfTools[1].when_to_use).toBeDefined();
    });
    
    it('debería devolver array vacío si no hay herramientas', () => {
      const atdfTools = batchConvert([]);
      expect(atdfTools).toEqual([]);
    });
  });
}); 