import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";
import { MCPTool } from "./tools/base.js";

// Import all 10 tools across the 4 categories
import { PerformanceTool, BatteryTool, ActiveWindowTool } from "./tools/monitoring.js";
import { VolumeTool, WifiToggleTool, PowerPlanTool } from "./tools/toggles.js";
import { AppLauncherTool, ClipboardTool } from "./tools/automation.js";
import { ScreenshotTool, WebSearchTool } from "./tools/perception.js";
import { HardwareAwarenessTool } from "./tools/hardware.js";
import { SafeCLITool } from "./tools/cli.js";
import { PlaySpotifyTool, PlayYouTubeTool } from "./tools/media.js";

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

    public registerTool(tool: MCPTool) {
        this.tools.set(tool.name, tool);
        console.log(`[MCP Registry] Registered tool: ${tool.name}`);
    }

    private setupHandlers() {
        this.server.setRequestHandler(ListToolsRequestSchema, async () => {
            return {
                tools: Array.from(this.tools.values()).map(t => ({
                    name: t.name,
                    description: t.description,
                    inputSchema: t.inputSchema
                }))
            };
        });

        this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
            const tool = this.tools.get(request.params.name);
            if (!tool) {
                throw new Error(`[MCP] FATAL: Tool ${request.params.name} is not registered.`);
            }
            try {
                const result = await tool.execute(request.params.arguments || {});
                return { content: [{ type: "text", text: result }] };
            } catch (error: any) {
                return { content: [{ type: "text", text: `Error: ${error.message}` }], isError: true };
            }
        });
    }

    public async start() {
        const transport = new StdioServerTransport();
        await this.server.connect(transport);
        console.log("Peter MCP Server connected and listening on stdio.");
    }
}

// Scaffold execution and register ALL tools
const server = new PeterMCPServer();

// 1. Monitoring & Hardware
server.registerTool(new PerformanceTool());
server.registerTool(new BatteryTool());
server.registerTool(new ActiveWindowTool());
server.registerTool(new HardwareAwarenessTool());

// 2. Toggles
server.registerTool(new VolumeTool());
server.registerTool(new WifiToggleTool());
server.registerTool(new PowerPlanTool());

// 3. Automation & CLI
server.registerTool(new AppLauncherTool());
server.registerTool(new ClipboardTool());
server.registerTool(new SafeCLITool());

// 4. Perception
server.registerTool(new ScreenshotTool());
server.registerTool(new WebSearchTool());

// 5. Media
server.registerTool(new PlaySpotifyTool());
server.registerTool(new PlayYouTubeTool());

server.start().catch(console.error);
