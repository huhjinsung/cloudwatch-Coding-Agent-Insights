#!/usr/bin/env python3
"""
Web Server Agent
A Flask-based web server that exposes Bedrock agents through REST APIs.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')

# Agent configurations
AGENT_CONFIGS = {
    "assistant": {
        "name": "General Assistant",
        "description": "A general-purpose AI assistant",
        "system_prompt": "You are a helpful AI assistant. Provide clear and concise responses."
    },
    "code_expert": {
        "name": "Code Expert",
        "description": "An AI expert in programming and software development",
        "system_prompt": "You are an expert programmer. Help users with coding questions and provide high-quality code examples."
    },
    "data_scientist": {
        "name": "Data Scientist",
        "description": "An AI expert in data analysis and machine learning",
        "system_prompt": "You are a data science expert. Help users analyze data and provide insights."
    }
}


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Bedrock Agent Web Server"
    })


@app.route('/agents', methods=['GET'])
def list_agents():
    """List available agents."""
    agents = []
    for agent_id, config in AGENT_CONFIGS.items():
        agents.append({
            "id": agent_id,
            "name": config["name"],
            "description": config["description"]
        })
    return jsonify({
        "status": "success",
        "agents": agents,
        "count": len(agents)
    })


@app.route('/agents/<agent_id>', methods=['GET'])
def get_agent_info(agent_id):
    """Get information about a specific agent."""
    if agent_id not in AGENT_CONFIGS:
        return jsonify({
            "status": "error",
            "message": f"Agent '{agent_id}' not found"
        }), 404

    config = AGENT_CONFIGS[agent_id]
    return jsonify({
        "status": "success",
        "id": agent_id,
        "name": config["name"],
        "description": config["description"]
    })


@app.route('/chat', methods=['POST'])
def chat():
    """Chat with an agent."""
    data = request.json

    agent_id = data.get('agent_id', 'assistant')
    message = data.get('message', '')

    if not message:
        return jsonify({
            "status": "error",
            "message": "Message is required"
        }), 400

    if agent_id not in AGENT_CONFIGS:
        return jsonify({
            "status": "error",
            "message": f"Agent '{agent_id}' not found"
        }), 404

    try:
        config = AGENT_CONFIGS[agent_id]

        response = bedrock_client.converse(
            modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
            system=[
                {
                    "type": "text",
                    "text": config["system_prompt"]
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": message
                        }
                    ]
                }
            ]
        )

        reply = response['output']['message']['content'][0]['text']

        return jsonify({
            "status": "success",
            "agent_id": agent_id,
            "message": message,
            "reply": reply,
            "timestamp": datetime.utcnow().isoformat(),
            "usage": {
                "input_tokens": response['usage']['inputTokens'],
                "output_tokens": response['usage']['outputTokens']
            }
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/chat/streaming', methods=['POST'])
def chat_streaming():
    """Chat with streaming response."""
    data = request.json

    agent_id = data.get('agent_id', 'assistant')
    message = data.get('message', '')

    if not message:
        return jsonify({
            "status": "error",
            "message": "Message is required"
        }), 400

    if agent_id not in AGENT_CONFIGS:
        return jsonify({
            "status": "error",
            "message": f"Agent '{agent_id}' not found"
        }), 404

    def generate():
        try:
            config = AGENT_CONFIGS[agent_id]

            response = bedrock_client.converse(
                modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
                system=[
                    {
                        "type": "text",
                        "text": config["system_prompt"]
                    }
                ],
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": message
                            }
                        ]
                    }
                ]
            )

            reply = response['output']['message']['content'][0]['text']

            yield f"data: {json.dumps({'status': 'streaming', 'chunk': reply})}\n\n"
            yield f"data: {json.dumps({'status': 'complete'})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'status': 'error', 'message': str(e)})}\n\n"

    return app.response_class(
        generate(),
        mimetype='text/event-stream'
    )


@app.route('/analyze', methods=['POST'])
def analyze_text():
    """Analyze text and provide insights."""
    data = request.json

    text = data.get('text', '')
    analysis_type = data.get('analysis_type', 'general')

    if not text:
        return jsonify({
            "status": "error",
            "message": "Text is required"
        }), 400

    analysis_prompts = {
        "sentiment": "Analyze the sentiment of this text and classify it as positive, negative, or neutral with explanation.",
        "summary": "Provide a concise summary of this text in 2-3 sentences.",
        "keywords": "Extract the top 5 keywords from this text.",
        "grammar": "Check the grammar and suggest corrections if needed.",
        "tone": "Analyze the tone and style of this text."
    }

    prompt = analysis_prompts.get(analysis_type, analysis_prompts["general"])
    full_prompt = f"{prompt}\n\nText: {text}"

    try:
        response = bedrock_client.converse(
            modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": full_prompt
                        }
                    ]
                }
            ]
        )

        analysis = response['output']['message']['content'][0]['text']

        return jsonify({
            "status": "success",
            "text": text[:100] + "..." if len(text) > 100 else text,
            "analysis_type": analysis_type,
            "analysis": analysis,
            "timestamp": datetime.utcnow().isoformat()
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/batch', methods=['POST'])
def batch_process():
    """Process multiple messages in batch."""
    data = request.json

    messages = data.get('messages', [])
    agent_id = data.get('agent_id', 'assistant')

    if not messages or not isinstance(messages, list):
        return jsonify({
            "status": "error",
            "message": "Messages must be a list"
        }), 400

    if agent_id not in AGENT_CONFIGS:
        return jsonify({
            "status": "error",
            "message": f"Agent '{agent_id}' not found"
        }), 404

    results = []
    config = AGENT_CONFIGS[agent_id]

    for idx, msg in enumerate(messages):
        try:
            response = bedrock_client.converse(
                modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
                system=[
                    {
                        "type": "text",
                        "text": config["system_prompt"]
                    }
                ],
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": msg
                            }
                        ]
                    }
                ]
            )

            reply = response['output']['message']['content'][0]['text']

            results.append({
                "index": idx,
                "message": msg,
                "reply": reply,
                "status": "success"
            })

        except Exception as e:
            results.append({
                "index": idx,
                "message": msg,
                "error": str(e),
                "status": "error"
            })

    return jsonify({
        "status": "success",
        "agent_id": agent_id,
        "total": len(messages),
        "processed": len([r for r in results if r["status"] == "success"]),
        "failed": len([r for r in results if r["status"] == "error"]),
        "results": results,
        "timestamp": datetime.utcnow().isoformat()
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        "status": "error",
        "message": "Endpoint not found"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        "status": "error",
        "message": "Internal server error"
    }), 500


if __name__ == '__main__':
    print("=" * 60)
    print("Bedrock Agent Web Server")
    print("=" * 60)
    print("\nAvailable Endpoints:")
    print("- GET  /health                 - Health check")
    print("- GET  /agents                 - List available agents")
    print("- GET  /agents/<agent_id>      - Get agent info")
    print("- POST /chat                   - Chat with agent")
    print("- POST /chat/streaming         - Streaming chat")
    print("- POST /analyze                - Analyze text")
    print("- POST /batch                  - Batch process messages")
    print("\nStarting server on http://0.0.0.0:5000")
    print("=" * 60)

    app.run(debug=True, host='0.0.0.0', port=5000)
