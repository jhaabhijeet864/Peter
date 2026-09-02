import { MCPTool } from "./base.js";
import { exec } from "child_process";
import { promisify } from "util";
import fetch from "node-fetch";
import fs from "fs/promises";

const execAsync = promisify(exec);

export class ScreenshotTool implements MCPTool {
    name = "take_screenshot";
    description = "Takes a fast snapshot of the screen using Python mss and returns the file path for vision analysis.";
    inputSchema = { type: "object", properties: {} as any };
    async execute(): Promise<string> {
        try {
            const script = `
import mss
with mss.mss() as sct:
    sct.shot(output='screen.png')
            `;
            await fs.writeFile("temp_snap.py", script);
            await execAsync("python temp_snap.py");
            return "Screenshot successfully saved to screen.png. Ready for vision pipeline analysis.";
        } catch(e: any) { return `Failed to take screenshot: ${e.message}`; }
    }
}

export class WebSearchTool implements MCPTool {
    name = "web_search";
    description = "Hits DuckDuckGo to fetch real-time answers and live information from the internet.";
    inputSchema = { 
        type: "object", 
        properties: { query: { type: "string" } },
        required: ["query"]
    };
    async execute(args: any): Promise<string> {
        try {
            const res = await fetch(`https://html.duckduckgo.com/html/?q=${encodeURIComponent(args.query)}`);
            const html = await res.text();
            
            const match = html.match(/<a class="result__snippet[^>]*>(.*?)<\/a>/);
            if (match && match[1]) {
                const cleanText = match[1].replace(/(<([^>]+)>)/gi, ""); // strip HTML tags
                return `Web Search Result:\n${cleanText}`;
            }
            return "No concise results found on the web.";
        } catch(e: any) { return `Web search failed: ${e.message}`; }
    }
}
