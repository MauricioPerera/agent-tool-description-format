const ATDFTool = require('../src/ATDFTool');

// Datos de prueba para una herramienta básica
const basicToolData = {
  tool_id: 'test_tool_v1',
  description: 'Herramienta de prueba',
  when_to_use: 'Usar durante pruebas',
  how_to_use: {
    inputs: [
      { name: 'test_param', type: 'string', description: 'Parámetro de prueba' }
    ],
    outputs: {
      success: 'Prueba exitosa',
      failure: [
        { code: 'test_error', description: 'Error de prueba' }
      ]
    }
  }
};

// Datos de prueba para una herramienta multilingüe
const multilingualToolData = {
  ...basicToolData,
  tool_id: 'multilingual_tool_v1',
  localization: {
    en: {
      description: 'Test tool',
      when_to_use: 'Use during testing'
    },
    pt: {
      description: 'Ferramenta de teste',
      when_to_use: 'Use durante testes'
    }
  }
};

describe('ATDFTool', () => {
  describe('Constructor', () => {
    test('Debería crear una instancia válida con datos básicos', () => {
      const tool = new ATDFTool(basicToolData);
      expect(tool).toBeInstanceOf(ATDFTool);
      expect(tool.toolId).toBe('test_tool_v1');
    });

    test('Debería lanzar error si faltan campos obligatorios', () => {
      const invalidData = { tool_id: 'invalid_tool' };
      expect(() => new ATDFTool(invalidData)).toThrow();
    });
  });

  describe('Propiedades básicas', () => {
    const tool = new ATDFTool(basicToolData);

    test('Debería obtener el ID correctamente', () => {
      expect(tool.toolId).toBe('test_tool_v1');
    });

    test('Debería obtener la descripción correctamente', () => {
      expect(tool.getDescription()).toBe('Herramienta de prueba');
    });

    test('Debería obtener when_to_use correctamente', () => {
      expect(tool.getWhenToUse()).toBe('Usar durante pruebas');
    });

    test('Debería obtener inputs correctamente', () => {
      expect(tool.inputs).toHaveLength(1);
      expect(tool.inputs[0].name).toBe('test_param');
    });

    test('Debería obtener outputs correctamente', () => {
      expect(tool.successMessage).toBe('Prueba exitosa');
      expect(tool.possibleErrors).toHaveLength(1);
      expect(tool.possibleErrors[0].code).toBe('test_error');
    });
  });

  describe('Propiedades opcionales y valores por defecto', () => {
    const optionalToolData = {
      tool_id: 'optional_tool_v1',
      description: 'Herramienta con campos opcionales',
      when_to_use: 'Usar cuando falten campos opcionales',
      how_to_use: {
        inputs: [
          {
            name: 'optional_param',
            type: 'string',
            description: 'Parámetro opcional',
            required: false
          }
        ],
        outputs: {}
      },
      metadata: { category: 'test' },
      prerequisites: { tools: ['base_tool'] },
      examples: [{ description: 'Ejemplo opcional' }]
    };

    const tool = new ATDFTool(optionalToolData);

    test('Debería indicar idiomas soportados cuando no hay localización', () => {
      expect(tool.supportedLanguages).toEqual(['default']);
    });

    test('Debería indicar que un idioma no está soportado cuando falta localización', () => {
      expect(tool.supportsLanguage('es')).toBe(false);
    });

    test('Debería devolver un arreglo vacío cuando no hay errores definidos', () => {
      expect(tool.possibleErrors).toEqual([]);
    });

    test('Debería devolver cadena vacía cuando no hay mensaje de éxito', () => {
      expect(tool.successMessage).toBe('');
    });

    test('Debería exponer metadatos, prerequisitos y ejemplos opcionales', () => {
      expect(tool.metadata).toEqual({ category: 'test' });
      expect(tool.prerequisites).toEqual({ tools: ['base_tool'] });
      expect(tool.examples).toEqual([{ description: 'Ejemplo opcional' }]);
    });

    test('Debería omitir parámetros marcados como no requeridos en el esquema', () => {
      const schema = tool.getInputSchema();
      expect(schema.required).not.toContain('optional_param');
    });
  });

  describe('Soporte multilingüe', () => {
    const tool = new ATDFTool(multilingualToolData);

    test('Debería detectar los idiomas soportados', () => {
      expect(tool.supportedLanguages).toContain('en');
      expect(tool.supportedLanguages).toContain('pt');
      expect(tool.supportedLanguages).toContain('default');
    });

    test('Debería verificar soporte de idioma correctamente', () => {
      expect(tool.supportsLanguage('en')).toBe(true);
      expect(tool.supportsLanguage('fr')).toBe(false);
    });

    test('Debería obtener descripciones en diferentes idiomas', () => {
      expect(tool.getDescription('en')).toBe('Test tool');
      expect(tool.getDescription('pt')).toBe('Ferramenta de teste');
      expect(tool.getDescription('fr')).toBe('Herramienta de prueba'); // Fallback al default
    });

    test('Debería obtener when_to_use en diferentes idiomas', () => {
      expect(tool.getWhenToUse('en')).toBe('Use during testing');
      expect(tool.getWhenToUse('pt')).toBe('Use durante testes');
      expect(tool.getWhenToUse('fr')).toBe('Usar durante pruebas'); // Fallback al default
    });
  });

  describe('Generación de esquema', () => {
    test('Debería generar un esquema de entrada válido', () => {
      const tool = new ATDFTool(basicToolData);
      const schema = tool.getInputSchema();
      
      expect(schema.type).toBe('object');
      expect(schema.properties).toHaveProperty('test_param');
      expect(schema.required).toContain('test_param');
    });

    test('Debería manejar esquemas de objetos complejos', () => {
      const complexToolData = {
        ...basicToolData,
        how_to_use: {
          inputs: [
            {
              name: 'config',
              type: 'object',
              schema: {
                properties: {
                  option1: { type: 'string' },
                  option2: { type: 'number' }
                },
                required: ['option1']
              },
              description: 'Configuración compleja'
            }
          ],
          outputs: basicToolData.how_to_use.outputs
        }
      };

      const tool = new ATDFTool(complexToolData);
      const schema = tool.getInputSchema();
      
      expect(schema.properties).toHaveProperty('config');
      expect(schema.properties.config).toHaveProperty('properties');
      expect(schema.properties.config.properties).toHaveProperty('option1');
      expect(schema.properties.config.properties).toHaveProperty('option2');
    });
  });

  describe('Serialización', () => {
    test('Debería convertirse a JSON correctamente', () => {
      const tool = new ATDFTool(basicToolData);
      const json = tool.toJSON();
      
      expect(json).toEqual(basicToolData);
    });
  });
});
