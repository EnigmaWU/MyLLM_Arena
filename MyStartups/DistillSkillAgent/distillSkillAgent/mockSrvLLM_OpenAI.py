
from flask import Flask, request, jsonify
import json
import time

app = Flask(__name__)

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    print(f"Received request: {request.json}")
    
    # Mock response
    mock_response = {
        "id": "chatcmpl-mock",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "gpt-4-mock",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": json.dumps([
                    {
                        "name": "mock-skill",
                        "description": "A mock skill extracted by the mock server.",
                        "what": "Demonstrate that the mock server works",
                        "why": "To test the agent without spending money",
                        "how": [
                            {"order": 1, "action": "Start mock server", "reasoning": "Need a server"},
                            {"order": 2, "action": "Run agent", "reasoning": "Need an agent"}
                        ],
                        "when": ["Testing", "Development"],
                        "examples": ["Example 1"],
                        "constraints": ["None for now"]
                    }
                ])
            },
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150
        }
    }
    
    return jsonify(mock_response)

if __name__ == '__main__':
    app.run(port=5001, debug=True)
