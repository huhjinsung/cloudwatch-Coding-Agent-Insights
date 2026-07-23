#!/usr/bin/env python3
"""
Data Analysis Agent
An agent that can analyze data, generate insights, and answer questions about datasets.
"""

import json
import boto3
import pandas as pd
from datetime import datetime, timedelta
from typing import Any


class DataAnalysisAgent:
    def __init__(self, region_name: str = "us-east-1"):
        self.bedrock_client = boto3.client('bedrock-runtime', region_name=region_name)
        self.data_store = {}

    def load_sample_data(self):
        """Load sample data for analysis."""
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        self.data_store['sales'] = pd.DataFrame({
            'date': dates,
            'region': ['North', 'South', 'East', 'West'] * (len(dates) // 4 + 1),
            'sales': [10000 + i * 100 for i in range(len(dates))],
            'customers': [100 + i * 2 for i in range(len(dates))]
        })

        self.data_store['weather'] = pd.DataFrame({
            'date': dates,
            'temperature': [15 + 10 * (i % 365) / 365 for i in range(len(dates))],
            'humidity': [60 + 20 * (i % 365) / 365 for i in range(len(dates))],
            'rainfall': [10 + 5 * (i % 365) / 365 for i in range(len(dates))]
        })

    def get_data_summary(self, dataset_name: str) -> dict:
        """Get summary statistics of a dataset."""
        if dataset_name not in self.data_store:
            return {"error": f"Dataset '{dataset_name}' not found"}

        df = self.data_store[dataset_name]
        summary = {
            "dataset_name": dataset_name,
            "shape": [df.shape[0], df.shape[1]],
            "columns": df.columns.tolist(),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "statistics": df.describe().to_dict(),
            "missing_values": df.isnull().sum().to_dict()
        }
        return summary

    def filter_data(self, dataset_name: str, column: str, value: Any, operation: str = "equals") -> dict:
        """Filter data based on conditions."""
        if dataset_name not in self.data_store:
            return {"error": f"Dataset '{dataset_name}' not found"}

        df = self.data_store[dataset_name]

        if operation == "equals":
            filtered = df[df[column] == value]
        elif operation == "greater_than":
            filtered = df[df[column] > value]
        elif operation == "less_than":
            filtered = df[df[column] < value]
        elif operation == "contains":
            filtered = df[df[column].astype(str).str.contains(str(value))]
        else:
            return {"error": f"Unknown operation: {operation}"}

        return {
            "rows_found": len(filtered),
            "sample_rows": filtered.head(5).to_dict(orient='records'),
            "filter_applied": {
                "dataset": dataset_name,
                "column": column,
                "value": str(value),
                "operation": operation
            }
        }

    def calculate_correlation(self, dataset_name: str) -> dict:
        """Calculate correlations between numeric columns."""
        if dataset_name not in self.data_store:
            return {"error": f"Dataset '{dataset_name}' not found"}

        df = self.data_store[dataset_name]
        numeric_cols = df.select_dtypes(include=['number']).columns

        if len(numeric_cols) < 2:
            return {"error": "Not enough numeric columns for correlation analysis"}

        correlation = df[numeric_cols].corr().to_dict()
        return {
            "dataset": dataset_name,
            "correlation_matrix": correlation,
            "numeric_columns": numeric_cols.tolist()
        }

    def aggregate_data(self, dataset_name: str, group_by: str, aggregate_func: str, column: str) -> dict:
        """Aggregate data by grouping."""
        if dataset_name not in self.data_store:
            return {"error": f"Dataset '{dataset_name}' not found"}

        df = self.data_store[dataset_name]

        if group_by not in df.columns:
            return {"error": f"Column '{group_by}' not found"}

        if column not in df.columns:
            return {"error": f"Column '{column}' not found"}

        if aggregate_func == "sum":
            result = df.groupby(group_by)[column].sum()
        elif aggregate_func == "mean":
            result = df.groupby(group_by)[column].mean()
        elif aggregate_func == "count":
            result = df.groupby(group_by).size()
        elif aggregate_func == "max":
            result = df.groupby(group_by)[column].max()
        elif aggregate_func == "min":
            result = df.groupby(group_by)[column].min()
        else:
            return {"error": f"Unknown aggregate function: {aggregate_func}"}

        return {
            "aggregation": {
                "dataset": dataset_name,
                "group_by": group_by,
                "aggregate_func": aggregate_func,
                "column": column
            },
            "results": result.to_dict()
        }

    def define_tools(self) -> list[dict]:
        """Define tools for data analysis."""
        return [
            {
                "toolUse": {
                    "toolName": "get_data_summary",
                    "description": "Get summary statistics and info about a dataset",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "dataset_name": {
                                    "type": "string",
                                    "description": "Name of the dataset (sales, weather)"
                                }
                            },
                            "required": ["dataset_name"]
                        }
                    }
                }
            },
            {
                "toolUse": {
                    "toolName": "filter_data",
                    "description": "Filter data based on column values",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "dataset_name": {
                                    "type": "string",
                                    "description": "Name of the dataset"
                                },
                                "column": {
                                    "type": "string",
                                    "description": "Column name to filter"
                                },
                                "value": {
                                    "type": "string",
                                    "description": "Value to filter by"
                                },
                                "operation": {
                                    "type": "string",
                                    "description": "Operation: equals, greater_than, less_than, contains"
                                }
                            },
                            "required": ["dataset_name", "column", "value"]
                        }
                    }
                }
            },
            {
                "toolUse": {
                    "toolName": "calculate_correlation",
                    "description": "Calculate correlation between numeric columns",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "dataset_name": {
                                    "type": "string",
                                    "description": "Name of the dataset"
                                }
                            },
                            "required": ["dataset_name"]
                        }
                    }
                }
            },
            {
                "toolUse": {
                    "toolName": "aggregate_data",
                    "description": "Aggregate data by grouping and applying a function",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "dataset_name": {
                                    "type": "string",
                                    "description": "Name of the dataset"
                                },
                                "group_by": {
                                    "type": "string",
                                    "description": "Column to group by"
                                },
                                "aggregate_func": {
                                    "type": "string",
                                    "description": "Function: sum, mean, count, max, min"
                                },
                                "column": {
                                    "type": "string",
                                    "description": "Column to aggregate"
                                }
                            },
                            "required": ["dataset_name", "group_by", "aggregate_func", "column"]
                        }
                    }
                }
            }
        ]

    def execute_tool(self, tool_name: str, tool_input: dict) -> str:
        """Execute a tool and return the result."""
        try:
            if tool_name == "get_data_summary":
                result = self.get_data_summary(tool_input.get("dataset_name", ""))
            elif tool_name == "filter_data":
                result = self.filter_data(
                    tool_input.get("dataset_name", ""),
                    tool_input.get("column", ""),
                    tool_input.get("value", ""),
                    tool_input.get("operation", "equals")
                )
            elif tool_name == "calculate_correlation":
                result = self.calculate_correlation(tool_input.get("dataset_name", ""))
            elif tool_name == "aggregate_data":
                result = self.aggregate_data(
                    tool_input.get("dataset_name", ""),
                    tool_input.get("group_by", ""),
                    tool_input.get("aggregate_func", ""),
                    tool_input.get("column", "")
                )
            else:
                result = {"error": f"Unknown tool: {tool_name}"}

            return json.dumps(result, default=str)
        except Exception as e:
            return json.dumps({"error": str(e)})

    def run_analysis(self, query: str, max_iterations: int = 5) -> str:
        """Run an analysis query with the agent."""
        tools = self.define_tools()
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": query
                    }
                ]
            }
        ]

        for iteration in range(max_iterations):
            response = self.bedrock_client.converse(
                modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
                messages=messages,
                tools=tools
            )

            stop_reason = response['stopReason']
            content = response['output']['message']['content']

            messages.append({
                "role": "assistant",
                "content": content
            })

            if stop_reason == "tool_use":
                tool_results = []

                for block in content:
                    if block.get("type") == "toolUse":
                        tool_name = block.get("toolName")
                        tool_input = block.get("input", {})

                        tool_result = self.execute_tool(tool_name, tool_input)

                        tool_results.append({
                            "type": "toolResult",
                            "toolUseId": block.get("toolUseId"),
                            "content": tool_result
                        })

                messages.append({
                    "role": "user",
                    "content": tool_results
                })

            else:
                for block in content:
                    if block.get("type") == "text":
                        return block.get("text", "")

        return "Max iterations reached"


if __name__ == "__main__":
    print("=" * 60)
    print("Data Analysis Agent")
    print("=" * 60)

    agent = DataAnalysisAgent()
    agent.load_sample_data()

    print("\nLoaded datasets:")
    for dataset_name in agent.data_store:
        df = agent.data_store[dataset_name]
        print(f"- {dataset_name}: {df.shape[0]} rows, {df.shape[1]} columns")

    # Example queries
    queries = [
        "Analyze the sales dataset and provide summary statistics",
        "What regions have the highest sales on average?",
        "Is there a correlation between weather conditions?"
    ]

    for query in queries:
        print(f"\n{'=' * 60}")
        print(f"Query: {query}")
        print(f"{'=' * 60}")
        try:
            result = agent.run_analysis(query)
            print(f"Result:\n{result}")
        except Exception as e:
            print(f"Error: {e}")
