import pytest
from core.guardrails import ActionGuardrail

def test_destructive_command_blocked():
    # By default, destructive commands should be blocked
    guard = ActionGuardrail(allow_destructive=False)
    assert guard.is_safe_command("Remove-Item C:\\important.txt") == False
    assert guard.is_safe_command("del /F /Q my_file") == False
    assert guard.is_safe_command("echo 'hello world'") == True

def test_destructive_command_allowed():
    # When explicitly allowed, they should pass
    guard = ActionGuardrail(allow_destructive=True)
    assert guard.is_safe_command("Remove-Item C:\\important.txt") == True

def test_path_restriction():
    guard = ActionGuardrail(restricted_dirs=["C:\\Windows", "C:\\Program Files"])
    
    # Absolute paths hitting the restriction
    assert guard.is_safe_path("C:\\Windows\\System32\\cmd.exe") == False
    assert guard.is_safe_path("C:\\Program Files\\App\\app.exe") == False
    
    # Safe paths
    assert guard.is_safe_path("D:\\Coding\\Projects\\Peter\\main.py") == True
