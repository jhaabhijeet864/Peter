import { MCPTool } from "./base.js";
import { exec } from "child_process";
import { promisify } from "util";

const execAsync = promisify(exec);

export class SafeCLITool implements MCPTool {
    name = "execute_safe_cli";
    description = "Executes safe, read-only Windows CLI commands (like ping, ipconfig, dir, systeminfo). Do NOT use for destructive actions.";
    inputSchema = { 
        type: "object", 
        properties: { command: { type: "string" } },
        required: ["command"]
    };
    
    async execute(args: any): Promise<string> {
        const cmd = args.command.toLowerCase();
        
        // Strict Deny-List Guardrails
        const blocked = ["del", "rm", "remove", "format", "stop-process", "kill", "invoke-webrequest", "curl", "wget", "shutdown", "restart"];
        if (blocked.some(b => cmd.includes(b))) {
            return "Error: Command rejected by Safe CLI guardrails. Destructive actions are strictly prohibited.";
        }
        
        try {
            const { stdout } = await execAsync(args.command);
            
            // We wrap the raw output in a specific XML-like tag.
            // The Python orchestrator will intercept this tag, instantly pop up the Terminal UI, 
            // and strip it from the TTS so Peter doesn't speak 500 lines of IP data aloud!
            return `<TERMINAL_OUTPUT>\n> ${args.command}\n\n${stdout.trim()}\n</TERMINAL_OUTPUT>`;
            
        } catch(e: any) { 
            return `<TERMINAL_OUTPUT>\n> ${args.command}\n\nCommand Failed: ${e.message}\n</TERMINAL_OUTPUT>`; 
        }
    }
}
