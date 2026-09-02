import subprocess
import os

class LocalLLM:
    """
    Python wrapper that bridges to the TypeScript Agent Core.
    Instead of calling Ollama directly, it offloads complex reasoning and 
    MCP tool execution to the TS process.
    """
    def __init__(self, model: str = None):
        # Phase 14 Update: Default to tool-capable coder model
        self.model = model or os.getenv("OLLAMA_MODEL", "qwen2.5-coder:3b")

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """
        Executes the TypeScript brain via IPC (subprocess).
        Ensures Peter can execute MCP tools before speaking.
        """
        import re
        import base64
        
        try:
            # Risk 5 Fix: Process-Tree Reaping to prevent Zombie MCP Node servers
            proc = subprocess.Popen(
                ["node", "dist/cli.mjs", prompt, self.model],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            try:
                stdout, stderr = proc.communicate(timeout=30)
                result_stdout = stdout
            except subprocess.TimeoutExpired:
                print(f"[Python Bridge] Orchestrator hung for 30s. Triggering Process Tree Kill on PID {proc.pid}.")
                # Native Windows process tree kill guarantees child Node processes/TCP sockets die
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], capture_output=True)
                proc.communicate() # flush pipes
                return "My typescript core experienced a 30-second processing timeout and was violently forcefully rebooted."
            
            # Parse the strict response marker to ignore TS console.log spam
            output = result_stdout
            if "__PETER_RESPONSE__:" in output:
                output = output.split("__PETER_RESPONSE__:")[1].strip()
            else:
                output = output.strip()
                
            # --- PHASE 12: TERMINAL UI INTERCEPTION ---
            if "<TERMINAL_OUTPUT>" in output:
                pattern = r"<TERMINAL_OUTPUT>(.*?)</TERMINAL_OUTPUT>"
                matches = re.findall(pattern, output, re.DOTALL)
                
                for match in matches:
                    # BUG 3 FIX: Use errors='replace' to prevent Windows ANSI encoding crashes
                    b64_text = base64.b64encode(match.strip().encode('utf-8', errors='replace')).decode('utf-8')
                    # Detached subprocess to run the Tkinter UI without blocking Python audio
                    subprocess.Popen(["python", "ui/terminal_popup.py", b64_text])
                
                # Replace the massive raw terminal output with a tiny TTS confirmation
                output = re.sub(pattern, "I have executed the command and displayed the terminal output on your screen.", output, flags=re.DOTALL)
                
            return output
            
        except subprocess.CalledProcessError as e:
            print(f"[Python Bridge Error] TS Process Failed:\n{e.stderr}")
            return "My typescript core experienced a critical fault."
        except FileNotFoundError:
            return "Critical Error: Node.js/npx not found in the system PATH."
