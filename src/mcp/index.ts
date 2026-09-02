import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";
import { MCPTool } from "./tools/base.js";

/**
 * Scalable MCP Tool Registry.
 * Handles dynamic tool routing, schema exposure, and execution limits.
 */
export class PeterMCPServer {
    private server: Server;
    private tools: Map<string, MCPTool> = new Map();

    constructor() {
        this.server = new Server(
            { name: "peter-mcp-core", version: "1.0.0" },
            { capabilities: { tools: {} } }
        );
        this.setupHandlers();
    }

    /** 
     * Dynamically registers a tool. This allows the System Tray UI to 
     * hot-swap tools on and off by dropping them from this registry.
     */
    public registerTool(tool: MCPTool) {
        this.tools.set(tool.name, tool);
    }

    private setupHandlers() {
        // Exposes the active tool schemas to the Agentic Orchestrator
        this.server.setRequestHandler(ListToolsRequestSchema, async () => {
            return {
                tools: Array.from(this.tools.values()).map(t => ({
                    name: t.name,
                    description: t.description,
                    inputSchema: t.inputSchema
                }))
            };
        });

        // Routes the LLM's tool request to the underlying native code
        this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
            const tool = this.tools.get(request.params.name);
            if (!tool) {
                throw new Error(`[MCP] FATAL: Tool ${request.params.name} is not registered or disabled.`);
            }
            
            try {
                const result = await tool.execute(request.params.arguments || {});
                return {
                    content: [{ type: "text", text: result }]
                };
            } catch (error: any) {
                return {
                    content: [{ type: "text", text: `Error: ${error.message}` }],
                    isError: true
                };
            }
        });
    }

    public async start() {
        const transport = new StdioServerTransport();
        await this.server.connect(transport);
        console.log("Peter MCP Server connected and listening on stdio.");
    }
}

// Scaffold execution (Tools will be injected dynamically by the orchestrator)
const server = new PeterMCPServer();
server.start().catch(console.error);
