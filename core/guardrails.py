import os
from pathlib import Path
from typing import List, Optional

class ActionGuardrail:
    """
    Safety guardrails to prevent Peter from executing harmful operations or 
    accessing restricted OS directories.
    """
    def __init__(self, allow_destructive: Optional[bool] = None, restricted_dirs: Optional[List[str]] = None):
        # Allow dependency injection for TDD, fallback to env vars
        if allow_destructive is None:
            self.allow_destructive = os.getenv("ALLOW_DESTRUCTIVE_COMMANDS", "false").lower() == "true"
        else:
            self.allow_destructive = allow_destructive

        if restricted_dirs is None:
            restricted_env = os.getenv("RESTRICTED_DIRECTORIES", "C:\\Windows")
            self.restricted_dirs = [Path(d.strip()) for d in restricted_env.split(",") if d.strip()]
        else:
            self.restricted_dirs = [Path(d) for d in restricted_dirs]

    def is_safe_command(self, command: str) -> bool:
        """Checks if a shell command contains destructive keywords."""
        if self.allow_destructive:
            return True
            
        destructive_keywords = ['del ', 'rmdir ', 'format ', 'diskpart', 'remove-item']
        command_lower = command.lower()
        
        for keyword in destructive_keywords:
            if keyword in command_lower:
                return False
        return True

    def is_safe_path(self, target_path: str) -> bool:
        """Checks if a path falls within a restricted directory."""
        try:
            target = Path(target_path).resolve()
            for restricted in self.restricted_dirs:
                # Check if target is relative to (inside) the restricted directory
                if restricted in target.parents or target == restricted:
                    return False
            return True
        except Exception:
            return False
