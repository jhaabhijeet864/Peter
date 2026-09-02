import { MCPTool } from "./base.js";
import { exec } from "child_process";
import { promisify } from "util";

const execAsync = promisify(exec);

export class HardwareAwarenessTool implements MCPTool {
    name = "check_hardware_gpu";
    description = "Reads deep hardware stats including NVIDIA GPU VRAM, Compute %, CUDA support, and General RAM. Makes Peter hardware-aware.";
    inputSchema = { type: "object", properties: {} as any };
    
    async execute(): Promise<string> {
        let output = "=== HARDWARE AWARENESS ===\n";
        
        // 1. General System Memory (RAM)
        try {
            const { stdout: mem } = await execAsync('wmic OS get FreePhysicalMemory,TotalVisibleMemorySize /value');
            output += `System Memory:\n${mem.trim()}\n\n`;
        } catch(e) {}

        // 2. Deep GPU & VRAM Diagnostics (Sentient NVIDIA detection)
        try {
            // Extracts exact model name, GPU load %, VRAM used, VRAM total, and temp
            const { stdout: gpu } = await execAsync('nvidia-smi --query-gpu=name,utilization.gpu,memory.used,memory.total,temperature.gpu --format=csv');
            output += `Dedicated GPU Status:\n${gpu.trim()}`;
        } catch(e) {
            output += "NVIDIA GPU not detected (nvidia-smi failed). System is likely utilizing AMD, Intel Integrated Graphics, or lacks CUDA support.";
        }
        
        return output;
    }
}
