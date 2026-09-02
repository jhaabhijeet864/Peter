import yaml
import os
from pathlib import Path
from dotenv import load_dotenv

def load_config(config_path="peter_config.yaml"):
    """Loads environment variables and the yaml config."""
    load_dotenv()
    path = Path(config_path)
    if not path.exists():
        return {}
    with open(path, 'r') as f:
        return yaml.safe_load(f) or {}

def update_env_variable(key: str, value: str, env_path=".env"):
    """Updates a key-value pair in the .env file and the live environment."""
    path = Path(env_path)
    if not path.exists():
        return
        
    key_found = False
    with open(path, 'r') as f:
        lines = f.readlines()
        
    with open(path, 'w') as f:
        for line in lines:
            if line.startswith(f"{key}="):
                f.write(f"{key}={value}\n")
                key_found = True
            else:
                f.write(line)
        if not key_found:
            f.write(f"{key}={value}\n")
            
    # Update the live environment immediately so the process sees it
    os.environ[key] = value
