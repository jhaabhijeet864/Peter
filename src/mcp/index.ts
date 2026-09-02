import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

/**
 * Peter's TypeScript MCP Server
 * The official Model Context Protocol ecosystem is deeply rooted in TypeScript.
 * This server will expose system operations and cloud fallbacks to the TS Agent Core.
 */
const server = new Server(
  {
    name: "peter-mcp-core",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// TODO: Register tools (e.g., Windows Task Manager, Wi-Fi toggles)

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.log("Peter TypeScript MCP Server running on stdio");
}

main().catch(console.error);
