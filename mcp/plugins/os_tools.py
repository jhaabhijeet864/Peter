import subprocess
import psutil

def open_app(app_name: str):
    """Launches an application via the OS shell."""
    print(f"Executing: {app_name}")
    try:
        # Warning: Using shell=True for simplicity; in production sanitize inputs.
        subprocess.Popen(app_name, shell=True)
        return {"status": "success", "message": f"Launched {app_name}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_system_stats():
    """Retrieves current CPU and RAM usage statistics."""
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory()
    return {
        "cpu_percent": cpu,
        "ram_percent": ram.percent,
        "ram_used_gb": round(ram.used / (1024**3), 2),
        "ram_total_gb": round(ram.total / (1024**3), 2)
    }

def register_tools():
    """Explicitly defines which functions to expose as MCP tools."""
    return {
        "open_app": open_app,
        "get_system_stats": get_system_stats
    }
