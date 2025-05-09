// Declaraciones para módulos sin archivos de tipos nativos

declare module 'mock-mcp-framework' {
  export class MCPTool {
    name: string;
    description: string;
    schema: Record<string, any>;
    constructor();
    execute(params: any): Promise<any>;
  }
  
  export class MCPServer {
    tools: MCPTool[];
    constructor();
    registerTool(tool: MCPTool): MCPServer;
    start(): Promise<MCPServer>;
  }
}

declare module '../../js/src/AtdfToMcp' {
  export function atdfToMcp(atdfTool: any, options?: any): any;
  export function convertAtdfFile(inputFile: string, outputFile?: string, options?: any): any;
  export function batchConvert(atdfTools: any[], outputDir: string, options?: any): any[];
} 