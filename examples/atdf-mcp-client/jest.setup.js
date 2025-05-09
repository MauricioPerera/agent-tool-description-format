// Setup para jest-fetch-mock
require('jest-fetch-mock').enableMocks();

// Silenciar los console.log en las pruebas
global.console = {
  ...console,
  log: jest.fn(),
  error: jest.fn(),
  warn: jest.fn(),
}; 