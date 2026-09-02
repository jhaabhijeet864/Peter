import { MCPTool } from "./base.js";
import { exec } from "child_process";
import { promisify } from "util";
import activeWindow from "active-win";

const execAsync = promisify(exec);

export class PerformanceTool implements MCPTool {
    name = "check_performance";
    description = "Reads current CPU and RAM usage to diagnose system lag.";
    inputSchema = { type: "object", properties: {} as any };
    async execute(): Promise<string> {
        try {
            const { stdout: cpu } = await execAsync('wmic cpu get loadpercentage /value');
            const { stdout: mem } = await execAsync('wmic OS get FreePhysicalMemory,TotalVisibleMemorySize /value');
            return `Performance Data:\n${cpu.trim()}\n${mem.trim()}`;
        } catch(e: any) { return `Failed to read performance: ${e.message}`; }
    }
}

export class BatteryTool implements MCPTool {
    name = "check_battery";
    description = "Reads current laptop battery percentage and charging state.";
    inputSchema = { type: "object", properties: {} as any };
    async execute(): Promise<string> {
        try {
            const { stdout } = await execAsync('wmic path Win32_Battery get EstimatedChargeRemaining,BatteryStatus /value');
            return `Battery Status:\n${stdout.trim()}\n(Status 2=AC/Charging, 1=Discharging)`;
        } catch(e: any) { return `Failed (You may be on a desktop PC): ${e.message}`; }
    }
}

export class ActiveWindowTool implements MCPTool {
    name = "get_active_window";
    description = "Tells Peter what application the user currently has open on their screen.";
    inputSchema = { type: "object", properties: {} as any };
    async execute(): Promise<string> {
        try {
            const win = await activeWindow();
            if (!win) return "No active window found.";
            return `Active Application: ${win.owner.name}\nWindow Title: ${win.title}`;
        } catch(e: any) { return `Failed to track window: ${e.message}`; }
    }
}
