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
        try:
            # We use npx tsx to execute the typescript file dynamically
            result = subprocess.run(
                ["npx", "tsx", "src/agent/cli.ts", prompt, self.model],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse the strict response marker to ignore TS console.log spam
            output = result.stdout
            if "__PETER_RESPONSE__:" in output:
                return output.split("__PETER_RESPONSE__:")[1].strip()
            
            return output.strip()
            
        except subprocess.CalledProcessError as e:
            print(f"[Python Bridge Error] TS Process Failed:\n{e.stderr}")
            return "My typescript core experienced a critical fault."
