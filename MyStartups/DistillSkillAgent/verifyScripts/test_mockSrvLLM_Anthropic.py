
import pytest
import subprocess
import time
import sys
import os
import signal
import requests
from pathlib import Path

@pytest.fixture
def mock_server_anthropic():
    """Start mock server in background."""
    # Start server
    proc = subprocess.Popen(
        [sys.executable, "-m", "distillSkillAgent.mockSrvLLM_Anthropic"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    time.sleep(2)
    
    yield proc
    
    # Teardown
    os.kill(proc.pid, signal.SIGTERM)

def test_mock_server_anthropic_interaction(mock_server_anthropic, cli_runner, sample_pdf_path, temp_dir):
    """Verify agent can talk to Anthropic mock server."""
    
    # Check if server is up
    try:
        response = requests.post(
            "http://localhost:5002/v1/messages", 
            json={
                "model": "claude-3-5-sonnet-20241022",
                "messages": [{"role": "user", "content": "hello"}],
                "max_tokens": 100
            }
        )
        assert response.status_code == 200
    except requests.exceptions.ConnectionError:
        pytest.fail("Mock server not accessible")

    # Run agent
    output_json = Path(temp_dir) / "mock_anthropic_output.json"
    result = cli_runner([
        "--input", str(sample_pdf_path),
        "--llm", "mockSrvLLM_Anthropic",
        "--output-json", str(output_json),
        "--verbose"
    ])
    
    # Print stderr if failed
    if result.returncode != 0:
        print(result.stderr)

    assert result.returncode == 0
    assert output_json.exists()
    
    import json
    with open(output_json) as f:
        data = json.load(f)
    
    # Check if we got the mock skill
    assert len(data) > 0
    assert data[0]["name"] == "mock-anthropic-skill"
