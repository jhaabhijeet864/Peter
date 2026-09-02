import subprocess
import os

class LocalLLM:
    """
    Python wrapper that bridges to the TypeScript Agent Core.
    Instead of calling Ollama directly, it offloads complex reasoning and 
    MCP tool execution to the TS process.
    """
    def __init__(self, model: str = None):
        self.model = model or os.getenv("OLLAMA_MODEL", "phi3:mini")

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """
        Executes the TypeScript brain via IPC (subprocess).
        Ensures Peter can execute MCP tools before speaking.
        """
        import re
        import base64
        
        try:
            # BUG 2 FIX: Enforce 30s timeout to prevent infinite zombie lockups if TS hangs
            # PHASE 14 FIX: Swapped npx tsx for native Node to bypass Node 24 ESM crashes
            result = subprocess.run(
                ["node", "dist/cli.mjs", prompt, self.model],
                capture_output=True,
                text=True,
                check=True,
                timeout=30 
            )
            
            # Parse the strict response marker to ignore TS console.log spam
            output = result.stdout
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
