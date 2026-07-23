#!/usr/bin/env python3
"""
Usage examples for Bedrock agents
"""

from bedrock_agent import invoke_bedrock_agent, run_agent_loop, define_sample_tools
from data_analysis_agent import DataAnalysisAgent
from aws_service_agent import AWSServiceAgent


def example_1_simple_invocation():
    """Example 1: Simple agent invocation"""
    print("\n" + "=" * 60)
    print("Example 1: Simple Agent Invocation")
    print("=" * 60)

    questions = [
        "What is machine learning?",
        "Explain quantum computing in simple terms",
        "What are the benefits of cloud computing?"
    ]

    for question in questions:
        print(f"\nQuestion: {question}")
        try:
            response = invoke_bedrock_agent(question)
            print(f"Answer: {response[:200]}...")
        except Exception as e:
            print(f"Error: {e}")


def example_2_data_analysis():
    """Example 2: Data analysis agent"""
    print("\n" + "=" * 60)
    print("Example 2: Data Analysis Agent")
    print("=" * 60)

    agent = DataAnalysisAgent()
    agent.load_sample_data()

    queries = [
        "Analyze the sales data and tell me the total sales by region",
        "What is the average number of customers per day?",
        "Compare the weather patterns and identify trends"
    ]

    for query in queries:
        print(f"\nQuery: {query}")
        try:
            result = agent.run_analysis(query, max_iterations=3)
            print(f"Result: {result[:200]}...")
        except Exception as e:
            print(f"Error: {e}")


def example_3_aws_resources():
    """Example 3: AWS service agent"""
    print("\n" + "=" * 60)
    print("Example 3: AWS Service Agent")
    print("=" * 60)

    agent = AWSServiceAgent()

    queries = [
        "Tell me about my AWS account",
        "List my S3 buckets and their sizes",
        "Show me my running EC2 instances"
    ]

    for query in queries:
        print(f"\nQuery: {query}")
        try:
            result = agent.run_query(query, max_iterations=3)
            print(f"Result: {result[:200]}...")
        except Exception as e:
            print(f"Error: {e}")


def example_4_agent_loop():
    """Example 4: Agentic loop with tool use"""
    print("\n" + "=" * 60)
    print("Example 4: Agentic Loop with Tool Use")
    print("=" * 60)

    prompt = """
    I'm planning a trip. Please:
    1. Check the weather in Seoul
    2. Calculate the distance from Seoul to Busan
    3. Check the weather in Busan
    Based on this information, recommend the best time to travel.
    """

    try:
        result = run_agent_loop(prompt, max_iterations=5)
        print(f"Result:\n{result}")
    except Exception as e:
        print(f"Error: {e}")


def example_5_data_filtering_and_analysis():
    """Example 5: Detailed data analysis"""
    print("\n" + "=" * 60)
    print("Example 5: Data Filtering and Analysis")
    print("=" * 60)

    agent = DataAnalysisAgent()
    agent.load_sample_data()

    # Get summary
    print("\n1. Dataset Summary:")
    summary = agent.get_data_summary('sales')
    print(f"   Rows: {summary['shape'][0]}, Columns: {summary['shape'][1]}")

    # Filter data
    print("\n2. Filter Data (North region):")
    filtered = agent.filter_data('sales', 'region', 'North')
    print(f"   Found {filtered['rows_found']} rows")

    # Calculate correlation
    print("\n3. Correlation Analysis:")
    correlation = agent.calculate_correlation('sales')
    print(f"   Columns: {correlation['numeric_columns']}")

    # Aggregate data
    print("\n4. Sales by Region:")
    aggregated = agent.aggregate_data('sales', 'region', 'sum', 'sales')
    for region, sales in aggregated['results'].items():
        print(f"   {region}: ${sales:,.0f}")


def example_6_batch_processing():
    """Example 6: Batch processing multiple requests"""
    print("\n" + "=" * 60)
    print("Example 6: Batch Processing")
    print("=" * 60)

    messages = [
        "What is Python?",
        "What is JavaScript?",
        "What is Go?",
        "What is Rust?"
    ]

    print("\nProcessing multiple questions in batch...")
    for i, msg in enumerate(messages, 1):
        try:
            response = invoke_bedrock_agent(msg)
            print(f"\n{i}. Q: {msg}")
            print(f"   A: {response[:150]}...")
        except Exception as e:
            print(f"Error processing message {i}: {e}")


def example_7_custom_analysis():
    """Example 7: Custom data analysis workflow"""
    print("\n" + "=" * 60)
    print("Example 7: Custom Analysis Workflow")
    print("=" * 60)

    agent = DataAnalysisAgent()
    agent.load_sample_data()

    # Get data summary
    sales_summary = agent.get_data_summary('sales')
    print(f"\nSales Dataset:")
    print(f"  Shape: {sales_summary['shape']}")
    print(f"  Columns: {', '.join(sales_summary['columns'])}")

    # Analyze by region
    regions = ['North', 'South', 'East', 'West']
    print(f"\nSales by Region:")
    for region in regions:
        filtered = agent.filter_data('sales', 'region', region)
        print(f"  {region}: {filtered['rows_found']} records")

    # Get correlation
    correlation = agent.calculate_correlation('sales')
    print(f"\nCorrelation Analysis: {len(correlation['numeric_columns'])} numeric columns")


def example_8_web_api_simulation():
    """Example 8: Simulate web API calls"""
    print("\n" + "=" * 60)
    print("Example 8: Web API Simulation")
    print("=" * 60)

    print("\nAvailable API Endpoints:")
    print("  GET  /health              - Health check")
    print("  GET  /agents              - List agents")
    print("  GET  /agents/<id>         - Get agent info")
    print("  POST /chat                - Chat with agent")
    print("  POST /analyze             - Analyze text")
    print("  POST /batch               - Batch processing")

    print("\nExample Request/Response:")
    print("\nRequest:")
    print("  POST /chat")
    print("  {")
    print('    "agent_id": "assistant",')
    print('    "message": "What is artificial intelligence?"')
    print("  }")
    print("\nResponse:")
    print("  {")
    print('    "status": "success",')
    print('    "reply": "Artificial intelligence is...",')
    print('    "usage": {"input_tokens": 10, "output_tokens": 150}')
    print("  }")


if __name__ == "__main__":
    print("\n" + "#" * 60)
    print("# Bedrock Agent Examples")
    print("#" * 60)

    examples = [
        ("Simple Invocation", example_1_simple_invocation),
        ("Data Analysis", example_2_data_analysis),
        ("AWS Resources", example_3_aws_resources),
        ("Agent Loop", example_4_agent_loop),
        ("Data Filtering", example_5_data_filtering_and_analysis),
        ("Batch Processing", example_6_batch_processing),
        ("Custom Analysis", example_7_custom_analysis),
        ("Web API", example_8_web_api_simulation)
    ]

    print("\nAvailable Examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")

    print("\n" + "#" * 60)
    print("Run examples by importing and calling the functions")
    print("or modify this script to select specific examples")
    print("#" * 60)
