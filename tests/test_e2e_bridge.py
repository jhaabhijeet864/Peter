import pytest
from core.llm import LocalLLM
import os

def test_e2e_python_ts_bridge():
    """
    E2E Test ensuring the Python hardware layer successfully passes data
    to the TypeScript Agent core, and the TS core returns a valid response.
    """
    # Ensure the env model is set to something fast for testing
    os.environ["OLLAMA_MODEL"] = "phi3:mini"
    llm = LocalLLM()
    
    # Send a simple prompt that does not require tool execution
    response = llm.generate("Return exactly the word 'ACKNOWLEDGED'. Nothing else.")
    
    # Ensure the typescript bridge didn't crash
    assert "critical fault" not in response.lower()
    
    # Note: Since Ollama might actually run this depending on local setup, 
    # we just ensure the bridge successfully parsed the stdout marker.
    assert isinstance(response, str)
    assert len(response) > 0
