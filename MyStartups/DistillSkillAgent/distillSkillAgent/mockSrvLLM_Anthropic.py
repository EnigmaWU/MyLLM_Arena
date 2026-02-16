
from flask import Flask, request, jsonify
import json
import time
import uuid

app = Flask(__name__)

@app.route('/v1/messages', methods=['POST'])
def messages():
    print(f"Received request: {request.json}")
    
    # Mock response structure for Anthropic Messages API
    mock_response = {
        "id": f"msg_{uuid.uuid4()}",
        "type": "message",
        "role": "assistant",
        "content": [
            {
                "type": "text",
                "text": json.dumps([{
                    "name": "mock-anthropic-skill",
                    "description": "A mock skill extracted by the Anthropic mock server.",
                    "what": "Demonstrate that the Anthropic mock server works",
                    "why": "To test the agent with Anthropic client",
                    "how": [
                        {"order": 1, "action": "Start Anthropic mock server", "reasoning": "Need a server"},
                        {"order": 2, "action": "Run agent with anthropic provider", "reasoning": "Need an agent"}
                    ],
                    "when": ["Testing Anthropic Integration"],
                    "examples": ["Example A"],
                    "constraints": ["None"]
                }])
            }
        ],
        "model": "claude-3-5-sonnet-20241022",
        "stop_reason": "end_turn",
        "stop_sequence": None,
        "usage": {
            "input_tokens": 100,
            "output_tokens": 50
        }
    }
    
    return jsonify(mock_response)

if __name__ == '__main__':
    app.run(port=5002, debug=True)
