/**
 * Abstract interface for all Model Context Protocol (MCP) Tools.
 * Ensures scalable, uniform integration of new capabilities.
 */
export interface MCPTool {
    /** The exact name of the tool exposed to the LLM */
    name: string;
    
    /** A detailed description guiding the LLM on when and how to use it */
    description: string;
    
    /** The JSON schema defining the arguments the tool expects */
    inputSchema: {
        type: "object";
        properties: Record<string, any>;
        required?: string[];
    };
    
    /** The native execution logic */
    execute(args: any): Promise<string>;
}
