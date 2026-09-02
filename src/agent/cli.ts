import { PeterAgent } from "./orchestrator.js";
import fs from "fs";

/**
 * Command Line Interface for the TypeScript Agent.
 * Acts as the E2E Integration bridge between Python (Hardware) and TypeScript (Brain).
 */
async function main() {
    const input = process.argv[2] || "status";
    const model = process.argv[3] || "qwen2.5-coder:3b";
    let systemPrompt = "";
    
    try {
        systemPrompt = fs.readFileSync("peter_system.md", "utf-8");
    } catch (e) {
        // Fallback if file isn't found during testing
    }

    const agent = new PeterAgent();
    // Execute intent and pipe result straight to stdout for Python to read
    const result = await agent.processIntent(input, model, systemPrompt);
    
    // Output strictly the result to prevent log pollution in Python
    console.log(`__PETER_RESPONSE__:${result}`);
}

main().catch(console.error);
