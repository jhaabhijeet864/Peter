import yaml
from pathlib import Path
from dotenv import load_dotenv

def load_config(config_path="peter_config.yaml"):
    """Loads environment variables and the yaml config."""
    # Load variables from .env into os.environ
    load_dotenv()
    
    path = Path(config_path)
    if not path.exists():
        return {}
    
    with open(path, 'r') as f:
        return yaml.safe_load(f) or {}
