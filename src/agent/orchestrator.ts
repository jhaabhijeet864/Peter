import ollama from 'ollama';
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

/**
 * The TypeScript Agent Orchestrator (Phase 5 & 6 Hybrid Router)
 * Implements the single-turn, low-latency MCP dispatch pattern.
 */
export class PeterAgent {
    private mcpClient: Client;
    private mcpConnected = false;

    constructor() {
        this.mcpClient = new Client(
            { name: "peter-agent", version: "1.0.0" },
            { capabilities: {} }
        );
    }

    /** Connects to the local PeterMCPServer via stdio */
    async connectMCP() {
        if (this.mcpConnected) return;
        const transport = new StdioClientTransport({
            command: "npx",
            args: ["tsx", "./src/mcp/index.ts"]
        });
        await this.mcpClient.connect(transport);
        this.mcpConnected = true;
        console.log("[TS Agent] Connected to native MCP Registry.");
    }

    /**
     * Processes the intent using the dynamically selected Ollama model.
     * @param transcribedText The STT output
     * @param modelName The dynamic model selected from the System Tray (.env)
     * @param systemPrompt The strict worker persona instructions
     */
    async processIntent(transcribedText: string, modelName: string, systemPrompt: string): Promise<string> {
        console.log(`[TS Agent] Processing intent via ${modelName}...`);
        await this.connectMCP();
        
        try {
            // 1. Fetch available tools dynamically from our MCP Registry
            const mcpList = await this.mcpClient.listTools();
            const ollamaTools = mcpList.tools.map(t => ({
                type: 'function',
                function: {
                    name: t.name,
                    description: t.description,
                    parameters: t.inputSchema as any
                }
            }));

            // 2. Classification & LLM Generation
            const response = await ollama.chat({
                model: modelName,
                messages: [
                    { role: 'system', content: systemPrompt },
                    { role: 'user', content: transcribedText }
                ],
                tools: ollamaTools,
                stream: false
            });

            // 3. Single-Turn Tool Execution
            if (response.message.tool_calls && response.message.tool_calls.length > 0) {
                // Grab the very first tool called to enforce single-turn limits
                const tool = response.message.tool_calls[0].function;
                console.log(`[TS Agent] LLM triggered tool execution: ${tool.name}`);
                
                const result = await this.mcpClient.callTool({
                    name: tool.name,
                    arguments: tool.arguments
                });

                // Directly return the tool's raw output to satisfy the "Worker" extreme brevity constraint
                // This skips a redundant second LLM call, making Peter lightning fast.
                if (result.isError) {
                    return `Tool error: ${result.content[0].text}`;
                }
                return result.content[0].text;
            }
            
            // 4. No tool needed, return direct conversational response
            return response.message.content;
            
        } catch (error) {
            console.error("[TS Agent Error] Failed to process intent:", error);
            return "I experienced a critical processing error.";
        }
    }
}
