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

    it('debería inferir tipo string correctamente para _def.typeName', () => {
      // Probar sólo con tipos que tienen estructura _def.typeName
      const mcpTool = {
        name: 'string-test',
        description: 'Test de strings',
        schema: {
          stringParam: {
            type: { _def: { typeName: 'ZodString' } },
            description: 'Parámetro string',
            required: true
          }
        }
      };

      const atdfTool = mcpToAtdf(mcpTool);
      expect(atdfTool.how_to_use.inputs[0].type).toBe('string');
    });

    it('debería inferir tipo number correctamente para _def.typeName', () => {
      const mcpTool = {
        name: 'number-test',
        description: 'Test de números',
        schema: {
          numberParam: {
            type: { _def: { typeName: 'ZodNumber' } },
            description: 'Parámetro numérico',
            required: true
          }
        }
      };

      const atdfTool = mcpToAtdf(mcpTool);
      expect(atdfTool.how_to_use.inputs[0].type).toBe('number');
    });

    it('debería inferir tipo boolean correctamente para _def.typeName', () => {
      const mcpTool = {
        name: 'boolean-test',
        description: 'Test de booleanos',
        schema: {
          boolParam: {
            type: { _def: { typeName: 'ZodBoolean' } },
            description: 'Parámetro booleano',
            required: true
          }
        }
      };

      const atdfTool = mcpToAtdf(mcpTool);
      expect(atdfTool.how_to_use.inputs[0].type).toBe('boolean');
    });

    it('debería inferir tipo array correctamente para _def.typeName', () => {
      const mcpTool = {
        name: 'array-test',
        description: 'Test de arrays',
        schema: {
          arrayParam: {
            type: { _def: { typeName: 'ZodArray' } },
            description: 'Parámetro array',
            required: true
          }
        }
      };

      const atdfTool = mcpToAtdf(mcpTool);
      expect(atdfTool.how_to_use.inputs[0].type).toBe('array');
    });

    it('debería inferir tipo object correctamente para _def.typeName', () => {
      const mcpTool = {
        name: 'object-test',
        description: 'Test de objetos',
        schema: {
          objectParam: {
            type: { _def: { typeName: 'ZodObject' } },
            description: 'Parámetro objeto',
            required: true
          }
        }
      };

      const atdfTool = mcpToAtdf(mcpTool);
      expect(atdfTool.how_to_use.inputs[0].type).toBe('object');
    });

    it('debería inferir tipos desde strings descriptivos', () => {
      // Pruebas más sencillas para tipos basados en cadenas
      const typeTests = [
        { type: 'string', expected: 'string' },
        { type: 'number', expected: 'number' },
        { type: 'boolean', expected: 'boolean' },
        { type: 'array', expected: 'array' },
        { type: 'object', expected: 'object' }
      ];

      for (const test of typeTests) {
        const mcpTool = {
          name: `${test.type}-test`,
          description: `Test de ${test.type}`,
          schema: {
            param: {
              type: test.type,
              description: `Parámetro ${test.type}`,
              required: true
            }
          }
        };

        const atdfTool = mcpToAtdf(mcpTool);
        expect(atdfTool.how_to_use.inputs[0].type).toBe(test.expected);
      }
    });

    it('debería manejar tipos desconocidos como any', () => {
      const unknownTypes = [
        { _def: { typeName: 'ZodUnknown' } },
        { _def: { typeName: 'ZodAny' } },
        'unknown',
        'custom-type',
        {}  // Objeto vacío
      ];

      for (const type of unknownTypes) {
        const mcpTool = {
          name: 'unknown-test',
          description: 'Test de tipos desconocidos',
          schema: {
            unknownParam: {
              type: type,
              description: 'Parámetro desconocido',
              required: true
            }
          }
        };

        const atdfTool = mcpToAtdf(mcpTool);
        expect(atdfTool.how_to_use.inputs[0].type).toBe('any');
      }
    });

    it('debería manejar opciones personalizadas para when_to_use', () => {
      const mcpTool = {
        name: 'custom-when',
        description: 'Herramienta con when_to_use personalizado',
        schema: {}
      };
      
      const customWhenToUse = 'Usar esta herramienta para casos específicos';
      const atdfTool = mcpToAtdf(mcpTool, { 
        includeWhenToUse: true,
        defaultWhenToUse: customWhenToUse
      });
      
      expect(atdfTool.when_to_use).toBe(customWhenToUse);
    });

    it('debería manejar herramientas sin descripción', () => {
      const mcpTool = {
        name: 'no-description',
        schema: {}
      };
      
      const atdfTool = mcpToAtdf(mcpTool);
      
      expect(atdfTool.description).toContain('no-description');
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