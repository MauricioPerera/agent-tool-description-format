// Jest setup file for global test configuration

// Global test timeout
jest.setTimeout(10000);

// Mock console methods in tests to reduce noise
global.console = {
  ...console,
  // Uncomment to ignore specific console methods during tests
  // log: jest.fn(),
  // debug: jest.fn(),
  // info: jest.fn(),
  warn: jest.fn(),
  error: jest.fn(),
};

// Global test utilities
global.testUtils = {
  // Helper to create mock ATDF tool
  createMockTool: (overrides = {}) => ({
    name: 'test-tool',
    description: 'A test tool',
    version: '1.0.0',
    input_schema: {
      type: 'object',
      properties: {
        query: { type: 'string' }
      },
      required: ['query']
    },
    output_schema: {
      type: 'object',
      properties: {
        result: { type: 'string' }
      }
    },
    ...overrides
  }),
  
  // Helper to create mock error response
  createMockError: (type = 'validation', message = 'Test error') => ({
    error: {
      type,
      message,
      details: {},
      timestamp: new Date().toISOString(),
      request_id: 'test-request-id'
    }
  }),
  
  // Helper to wait for async operations
  wait: (ms = 100) => new Promise(resolve => setTimeout(resolve, ms)),
};

// Setup for async tests
beforeEach(() => {
  // Clear all mocks before each test
  jest.clearAllMocks();
});

afterEach(() => {
  // Clean up after each test
  jest.restoreAllMocks();
});