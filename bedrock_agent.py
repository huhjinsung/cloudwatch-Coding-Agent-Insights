#!/usr/bin/env python3
"""
AWS Bedrock Agent Sample Code
A sample agent that uses Claude model via AWS Bedrock API.
"""

import json
import boto3
from typing import Any

# Initialize Bedrock client
bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')

def invoke_bedrock_agent(prompt: str, model_id: str = "anthropic.claude-3-5-sonnet-20241022-v2:0") -> str:
    """
    Invoke a simple agent with Bedrock using Claude model.

    Args:
        prompt: The input prompt for the agent
        model_id: The model ID to use (default: Claude 3.5 Sonnet)

    Returns:
        The agent's response
    """
    message = bedrock_client.converse(
        modelId=model_id,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
    )

    return message['output']['message']['content'][0]['text']


def bedrock_agent_with_tools(prompt: str, tools: list[dict] = None) -> dict:
    """
    Invoke Bedrock agent with tool use capability.

    Args:
        prompt: The input prompt
        tools: List of tool definitions for the agent to use

    Returns:
        Response dict containing the agent's response and any tool calls
    """
    if tools is None:
        tools = []

    system_prompt = """You are a helpful AI assistant powered by AWS Bedrock.
You can help users with various tasks including:
- Answering questions
- Analyzing data
- Providing recommendations
- Using available tools to accomplish tasks

When responding, be clear and concise."""

    message = bedrock_client.converse(
        modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
        system=[
            {
                "type": "text",
                "text": system_prompt
            }
        ],
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ],
        tools=tools if tools else None
    )

    return {
        "status": message['stopReason'],
        "response": message['output']['message']['content'],
        "usage": message['usage']
    }


def define_sample_tools() -> list[dict]:
    """
    Define sample tools that the agent can use.

    Returns:
        List of tool definitions
    """
    return [
        {
            "toolUse": {
                "toolName": "get_weather",
                "description": "Get current weather for a location",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "City name"
                            }
                        },
                        "required": ["location"]
                    }
                }
            }
        },
        {
            "toolUse": {
                "toolName": "calculate_distance",
                "description": "Calculate distance between two locations",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "from_location": {
                                "type": "string",
                                "description": "Starting location"
                            },
                            "to_location": {
                                "type": "string",
                                "description": "Destination location"
                            }
                        },
                        "required": ["from_location", "to_location"]
                    }
                }
            }
        }
    ]


def handle_tool_use(tool_name: str, tool_input: dict) -> str:
    """
    Handle tool execution - simulate tool results.

    Args:
        tool_name: Name of the tool to execute
        tool_input: Input parameters for the tool

    Returns:
        Tool result as string
    """
    if tool_name == "get_weather":
        location = tool_input.get("location", "Unknown")
        return json.dumps({
            "location": location,
            "temperature": "22°C",
            "condition": "Partly Cloudy",
            "humidity": "65%"
        })

    elif tool_name == "calculate_distance":
        from_loc = tool_input.get("from_location", "Unknown")
        to_loc = tool_input.get("to_location", "Unknown")
        return json.dumps({
            "from": from_loc,
            "to": to_loc,
            "distance_km": 150,
            "estimated_time": "2 hours"
        })

    return json.dumps({"error": f"Unknown tool: {tool_name}"})


def run_agent_loop(initial_prompt: str, max_iterations: int = 5) -> str:
    """
    Run an agentic loop that can use tools multiple times.

    Args:
        initial_prompt: The initial user prompt
        max_iterations: Maximum number of iterations

    Returns:
        Final response from the agent
    """
    tools = define_sample_tools()
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": initial_prompt
                }
            ]
        }
    ]

    for iteration in range(max_iterations):
        print(f"\n--- Iteration {iteration + 1} ---")

        response = bedrock_client.converse(
            modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
            messages=messages,
            tools=tools
        )

        stop_reason = response['stopReason']
        content = response['output']['message']['content']

        print(f"Stop reason: {stop_reason}")

        # Add assistant response to messages
        messages.append({
            "role": "assistant",
            "content": content
        })

        # Check if agent wants to use tools
        if stop_reason == "tool_use":
            tool_results = []

            for block in content:
                if block.get("type") == "toolUse":
                    tool_name = block.get("toolName")
                    tool_input = block.get("input", {})

                    print(f"Tool called: {tool_name}")
                    print(f"Tool input: {json.dumps(tool_input, indent=2)}")

                    # Execute tool
                    tool_result = handle_tool_use(tool_name, tool_input)
                    print(f"Tool result: {tool_result}")

                    tool_results.append({
                        "type": "toolResult",
                        "toolUseId": block.get("toolUseId"),
                        "content": tool_result
                    })

            # Add tool results to messages
            messages.append({
                "role": "user",
                "content": tool_results
            })

        else:
            # Agent has finished
            for block in content:
                if block.get("type") == "text":
                    return block.get("text", "")

    return "Max iterations reached"


if __name__ == "__main__":
    print("=" * 60)
    print("AWS Bedrock Agent Sample")
    print("=" * 60)

    # Example 1: Simple invoke
    print("\n1. Simple Agent Invocation:")
    print("-" * 60)
    try:
        response = invoke_bedrock_agent("What is machine learning?")
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")

    # Example 2: Agent with tools
    print("\n2. Agent with Tools:")
    print("-" * 60)
    try:
        tools = define_sample_tools()
        result = bedrock_agent_with_tools(
            "What's the weather in Seoul and how far is it from Busan?",
            tools
        )
        print(f"Status: {result['status']}")
        print(f"Response: {json.dumps(result['response'], indent=2, ensure_ascii=False)}")
        print(f"Usage: {result['usage']}")
    except Exception as e:
        print(f"Error: {e}")

    # Example 3: Agentic loop
    print("\n3. Agentic Loop with Tool Use:")
    print("-" * 60)
    try:
        final_response = run_agent_loop("I want to travel from Seoul to Busan. Please check the weather and calculate the distance.")
        print(f"\nFinal Response:\n{final_response}")
    except Exception as e:
        print(f"Error: {e}")
