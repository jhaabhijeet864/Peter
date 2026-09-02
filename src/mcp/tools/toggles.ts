import { MCPTool } from "./base.js";
import { exec } from "child_process";
import { promisify } from "util";
const execAsync = promisify(exec);

export class VolumeTool implements MCPTool {
    name = "set_volume";
    description = "Mutes the system or changes volume.";
    inputSchema = { 
        type: "object", 
        properties: { action: { type: "string", enum: ["mute", "unmute"] } },
        required: ["action"]
    };
    async execute(args: any): Promise<string> {
        try {
            // Emulates pressing the mute media key using PowerShell
            await execAsync(`powershell -c "$obj = new-object -com wscript.shell; $obj.SendKeys([char]173)"`);
            return `System volume mute toggled via media keys.`;
        } catch(e: any) { return `Failed: ${e.message}`; }
    }
}

export class WifiToggleTool implements MCPTool {
    name = "toggle_wifi";
    description = "Turns Wi-Fi adapter on or off. Requires Administrator privileges.";
    inputSchema = { 
        type: "object", 
        properties: { state: { type: "string", enum: ["enable", "disable"] } },
        required: ["state"]
    };
    async execute(args: any): Promise<string> {
        try {
            await execAsync(`netsh interface set interface name="Wi-Fi" admin=${args.state}`);
            return `Wi-Fi successfully set to ${args.state}.`;
        } catch(e: any) { return `Failed to toggle Wi-Fi. (Admin privileges likely required in Windows).`; }
    }
}

export class PowerPlanTool implements MCPTool {
    name = "set_power_plan";
    description = "Swaps laptop into Battery Saver or High Performance mode.";
    inputSchema = { 
        type: "object", 
        properties: { plan: { type: "string", enum: ["saver", "performance", "balanced"] } },
        required: ["plan"]
    };
    async execute(args: any): Promise<string> {
        try {
            let guid = "381b4222-f694-41f0-9685-ff5bb260df2e"; // balanced
            if(args.plan === "saver") guid = "a1841308-3541-4fab-bc81-f71556f20b4a";
            if(args.plan === "performance") guid = "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c";
            
            await execAsync(`powercfg /setactive ${guid}`);
            return `Power plan successfully switched to ${args.plan}.`;
        } catch(e: any) { return `Failed to set power plan: ${e.message}`; }
    }
}
