#!/usr/bin/env python3
"""
AWS Service Agent
An agent that can interact with various AWS services like S3, EC2, CloudWatch, etc.
"""

import json
import boto3
from typing import Any
from datetime import datetime, timedelta


class AWSServiceAgent:
    def __init__(self, region_name: str = "us-east-1"):
        self.bedrock_client = boto3.client('bedrock-runtime', region_name=region_name)
        self.s3_client = boto3.client('s3', region_name=region_name)
        self.ec2_client = boto3.client('ec2', region_name=region_name)
        self.cloudwatch_client = boto3.client('cloudwatch', region_name=region_name)
        self.region = region_name

    def list_s3_buckets(self) -> dict:
        """List all S3 buckets."""
        try:
            response = self.s3_client.list_buckets()
            buckets = [{'name': b['Name'], 'created': b['CreationDate'].isoformat()} for b in response.get('Buckets', [])]
            return {
                "status": "success",
                "bucket_count": len(buckets),
                "buckets": buckets
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_s3_bucket_size(self, bucket_name: str) -> dict:
        """Get total size of S3 bucket."""
        try:
            response = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/S3',
                MetricName='BucketSizeBytes',
                Dimensions=[
                    {'Name': 'BucketName', 'Value': bucket_name},
                    {'Name': 'StorageType', 'Value': 'StandardStorage'}
                ],
                StartTime=datetime.utcnow() - timedelta(days=1),
                EndTime=datetime.utcnow(),
                Period=86400,
                Statistics=['Average']
            )

            datapoints = response.get('Datapoints', [])
            if datapoints:
                size_bytes = datapoints[0]['Average']
                size_gb = size_bytes / (1024 ** 3)
                return {
                    "status": "success",
                    "bucket_name": bucket_name,
                    "size_bytes": size_bytes,
                    "size_gb": round(size_gb, 2)
                }
            else:
                return {
                    "status": "success",
                    "bucket_name": bucket_name,
                    "message": "No data available"
                }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def list_ec2_instances(self) -> dict:
        """List all EC2 instances."""
        try:
            response = self.ec2_client.describe_instances()
            instances = []

            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    instances.append({
                        'instance_id': instance['InstanceId'],
                        'instance_type': instance['InstanceType'],
                        'state': instance['State']['Name'],
                        'launch_time': instance['LaunchTime'].isoformat()
                    })

            return {
                "status": "success",
                "instance_count": len(instances),
                "instances": instances
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_ec2_instance_details(self, instance_id: str) -> dict:
        """Get detailed information about an EC2 instance."""
        try:
            response = self.ec2_client.describe_instances(InstanceIds=[instance_id])

            if not response['Reservations']:
                return {"status": "error", "message": f"Instance {instance_id} not found"}

            instance = response['Reservations'][0]['Instances'][0]
            return {
                "status": "success",
                "instance_id": instance['InstanceId'],
                "instance_type": instance['InstanceType'],
                "state": instance['State']['Name'],
                "public_ip": instance.get('PublicIpAddress', 'N/A'),
                "private_ip": instance.get('PrivateIpAddress', 'N/A'),
                "launch_time": instance['LaunchTime'].isoformat(),
                "availability_zone": instance['Placement']['AvailabilityZone']
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_cloudwatch_metrics(self, namespace: str, metric_name: str, hours: int = 1) -> dict:
        """Get CloudWatch metrics."""
        try:
            response = self.cloudwatch_client.get_metric_statistics(
                Namespace=namespace,
                MetricName=metric_name,
                StartTime=datetime.utcnow() - timedelta(hours=hours),
                EndTime=datetime.utcnow(),
                Period=300,
                Statistics=['Average', 'Maximum', 'Minimum']
            )

            datapoints = response.get('Datapoints', [])
            return {
                "status": "success",
                "namespace": namespace,
                "metric_name": metric_name,
                "datapoint_count": len(datapoints),
                "datapoints": sorted(datapoints, key=lambda x: x['Timestamp'], reverse=True)[:10]
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_account_info(self) -> dict:
        """Get basic AWS account information."""
        try:
            sts_client = boto3.client('sts')
            identity = sts_client.get_caller_identity()
            return {
                "status": "success",
                "account_id": identity['Account'],
                "user_arn": identity['Arn'],
                "region": self.region
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def define_tools(self) -> list[dict]:
        """Define tools for AWS service operations."""
        return [
            {
                "toolUse": {
                    "toolName": "list_s3_buckets",
                    "description": "List all S3 buckets in the account",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {}
                        }
                    }
                }
            },
            {
                "toolUse": {
                    "toolName": "get_s3_bucket_size",
                    "description": "Get the size of an S3 bucket",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "bucket_name": {
                                    "type": "string",
                                    "description": "Name of the S3 bucket"
                                }
                            },
                            "required": ["bucket_name"]
                        }
                    }
                }
            },
            {
                "toolUse": {
                    "toolName": "list_ec2_instances",
                    "description": "List all EC2 instances",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {}
                        }
                    }
                }
            },
            {
                "toolUse": {
                    "toolName": "get_ec2_instance_details",
                    "description": "Get detailed information about an EC2 instance",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "instance_id": {
                                    "type": "string",
                                    "description": "EC2 instance ID"
                                }
                            },
                            "required": ["instance_id"]
                        }
                    }
                }
            },
            {
                "toolUse": {
                    "toolName": "get_cloudwatch_metrics",
                    "description": "Get CloudWatch metrics",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "namespace": {
                                    "type": "string",
                                    "description": "CloudWatch namespace (e.g., AWS/EC2, AWS/S3)"
                                },
                                "metric_name": {
                                    "type": "string",
                                    "description": "Metric name"
                                },
                                "hours": {
                                    "type": "integer",
                                    "description": "Number of hours to look back"
                                }
                            },
                            "required": ["namespace", "metric_name"]
                        }
                    }
                }
            },
            {
                "toolUse": {
                    "toolName": "get_account_info",
                    "description": "Get AWS account information",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {}
                        }
                    }
                }
            }
        ]

    def execute_tool(self, tool_name: str, tool_input: dict) -> str:
        """Execute a tool and return the result."""
        try:
            if tool_name == "list_s3_buckets":
                result = self.list_s3_buckets()
            elif tool_name == "get_s3_bucket_size":
                result = self.get_s3_bucket_size(tool_input.get("bucket_name", ""))
            elif tool_name == "list_ec2_instances":
                result = self.list_ec2_instances()
            elif tool_name == "get_ec2_instance_details":
                result = self.get_ec2_instance_details(tool_input.get("instance_id", ""))
            elif tool_name == "get_cloudwatch_metrics":
                result = self.get_cloudwatch_metrics(
                    tool_input.get("namespace", ""),
                    tool_input.get("metric_name", ""),
                    tool_input.get("hours", 1)
                )
            elif tool_name == "get_account_info":
                result = self.get_account_info()
            else:
                result = {"status": "error", "message": f"Unknown tool: {tool_name}"}

            return json.dumps(result, default=str)
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})

    def run_query(self, query: str, max_iterations: int = 5) -> str:
        """Run a query with the agent."""
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
    print("AWS Service Agent")
    print("=" * 60)

    agent = AWSServiceAgent()

    queries = [
        "What AWS resources do I have?",
        "Tell me about my EC2 instances",
        "What's my AWS account ID?"
    ]

    for query in queries:
        print(f"\n{'=' * 60}")
        print(f"Query: {query}")
        print(f"{'=' * 60}")
        try:
            result = agent.run_query(query)
            print(f"Result:\n{result}")
        except Exception as e:
            print(f"Error: {e}")
