
import pytest
import subprocess
import time
import sys
import os
import signal
import requests
from pathlib import Path

@pytest.fixture
def mock_server():
    """Start mock server in background."""
    # Start server
    proc = subprocess.Popen(
        [sys.executable, "-m", "distillSkillAgent.mockSrvLLM_OpenAI"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    time.sleep(2)
    
    yield proc
    
    # Teardown
    os.kill(proc.pid, signal.SIGTERM)

def test_mock_server_interaction(mock_server, cli_runner, sample_pdf_path, temp_dir):
    """Verify agent can talk to mock server."""
    
    # Check if server is up
    try:
        # The mock server doesn't have a health check, but we can try to connect
        # or just assume it's up if sleep worked. 
        # Actually let's try to hit the endpoint with a dummy request to confirm it's running
        response = requests.post(
            "http://localhost:5001/v1/chat/completions", 
            json={"messages": [{"role": "user", "content": "hello"}]}
        )
        assert response.status_code == 200
    except requests.exceptions.ConnectionError:
        pytest.fail("Mock server not accessible")

    # Run agent
    output_json = Path(temp_dir) / "mock_output.json"
    result = cli_runner([
        "--input", str(sample_pdf_path),
        "--llm", "mockSrvLLM_OpenAI",
        "--output-json", str(output_json),
        "--verbose"
    ])
    
    assert result.returncode == 0
    assert output_json.exists()
    
    import json
    with open(output_json) as f:
        data = json.load(f)
    
    # Check if we got the mock skill
    assert len(data) > 0
    assert data[0]["name"] == "mock-skill"
