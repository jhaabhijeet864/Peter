import { MCPTool } from "./base.js";
import { exec } from "child_process";
import { promisify } from "util";
import clipboard from "clipboardy";

const execAsync = promisify(exec);

export class AppLauncherTool implements MCPTool {
    name = "launch_app";
    description = "Opens specific applications on Windows (e.g. 'notepad', 'calc', 'chrome').";
    inputSchema = { 
        type: "object", 
        properties: { app_name: { type: "string" } },
        required: ["app_name"]
    };
    async execute(args: any): Promise<string> {
        try {
            await execAsync(`start ${args.app_name}`);
            return `Successfully launched application: ${args.app_name}.`;
        } catch(e: any) { return `Failed to launch ${args.app_name}: ${e.message}`; }
    }
}

export class ClipboardTool implements MCPTool {
    name = "read_clipboard";
    description = "Reads the last text copied to the Windows clipboard.";
    inputSchema = { type: "object", properties: {} as any };
    async execute(): Promise<string> {
        try {
            const text = await clipboard.read();
            return text ? `Clipboard contents:\n${text}` : "Clipboard is currently empty.";
        } catch(e: any) { return `Failed to read clipboard: ${e.message}`; }
    }
}
