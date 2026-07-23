#!/usr/bin/env python3
"""
Monitoring Agent
An agent that monitors system health, performance metrics, and sends alerts.
"""

import json
import boto3
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class MetricStatus(Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class SystemMetric:
    name: str
    value: float
    unit: str
    threshold_warning: float
    threshold_critical: float
    timestamp: str
    status: str

    def to_dict(self):
        return asdict(self)


class MonitoringAgent:
    def __init__(self, region_name: str = "us-east-1"):
        self.bedrock_client = boto3.client('bedrock-runtime', region_name=region_name)
        self.cloudwatch_client = boto3.client('cloudwatch', region_name=region_name)
        self.metrics_history = []
        self.alerts = []
        self.thresholds = {
            'cpu': {'warning': 70, 'critical': 90},
            'memory': {'warning': 80, 'critical': 95},
            'disk': {'warning': 75, 'critical': 90},
            'network': {'warning': 80, 'critical': 95}
        }

    def get_cpu_metrics(self) -> SystemMetric:
        """Get CPU usage metrics."""
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()

        status = self._determine_status(
            cpu_percent,
            self.thresholds['cpu']['warning'],
            self.thresholds['cpu']['critical']
        )

        metric = SystemMetric(
            name="cpu_usage",
            value=cpu_percent,
            unit="%",
            threshold_warning=self.thresholds['cpu']['warning'],
            threshold_critical=self.thresholds['cpu']['critical'],
            timestamp=datetime.utcnow().isoformat(),
            status=status
        )

        self.metrics_history.append(metric)
        return metric

    def get_memory_metrics(self) -> SystemMetric:
        """Get memory usage metrics."""
        memory = psutil.virtual_memory()
        memory_percent = memory.percent

        status = self._determine_status(
            memory_percent,
            self.thresholds['memory']['warning'],
            self.thresholds['memory']['critical']
        )

        metric = SystemMetric(
            name="memory_usage",
            value=memory_percent,
            unit="%",
            threshold_warning=self.thresholds['memory']['warning'],
            threshold_critical=self.thresholds['memory']['critical'],
            timestamp=datetime.utcnow().isoformat(),
            status=status
        )

        self.metrics_history.append(metric)
        return metric

    def get_disk_metrics(self) -> SystemMetric:
        """Get disk usage metrics."""
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent

        status = self._determine_status(
            disk_percent,
            self.thresholds['disk']['warning'],
            self.thresholds['disk']['critical']
        )

        metric = SystemMetric(
            name="disk_usage",
            value=disk_percent,
            unit="%",
            threshold_warning=self.thresholds['disk']['warning'],
            threshold_critical=self.thresholds['disk']['critical'],
            timestamp=datetime.utcnow().isoformat(),
            status=status
        )

        self.metrics_history.append(metric)
        return metric

    def get_process_metrics(self, process_name: Optional[str] = None) -> Dict:
        """Get process metrics."""
        processes = []

        if process_name:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    if process_name.lower() in proc.info['name'].lower():
                        processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'cpu_percent': proc.info['cpu_percent'] or 0,
                            'memory_percent': proc.info['memory_percent'] or 0
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        else:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cpu_percent': proc.info['cpu_percent'] or 0,
                        'memory_percent': proc.info['memory_percent'] or 0
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

        return {
            'status': 'success',
            'process_count': len(processes),
            'processes': sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:10]
        }

    def get_network_metrics(self) -> Dict:
        """Get network metrics."""
        net_io = psutil.net_io_counters()
        return {
            'status': 'success',
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv,
            'errors_in': net_io.errin,
            'errors_out': net_io.errout,
            'dropped_in': net_io.dropin,
            'dropped_out': net_io.dropout
        }

    def get_system_health(self) -> Dict:
        """Get overall system health."""
        cpu = self.get_cpu_metrics()
        memory = self.get_memory_metrics()
        disk = self.get_disk_metrics()

        statuses = [cpu.status, memory.status, disk.status]
        overall_status = self._aggregate_status(statuses)

        return {
            'status': 'success',
            'overall_health': overall_status,
            'timestamp': datetime.utcnow().isoformat(),
            'metrics': {
                'cpu': cpu.to_dict(),
                'memory': memory.to_dict(),
                'disk': disk.to_dict()
            }
        }

    def put_cloudwatch_metric(self, metric_name: str, value: float, unit: str = "Percent") -> Dict:
        """Put a custom metric to CloudWatch."""
        try:
            self.cloudwatch_client.put_metric_data(
                Namespace='BedrockAgent',
                MetricData=[
                    {
                        'MetricName': metric_name,
                        'Value': value,
                        'Unit': unit,
                        'Timestamp': datetime.utcnow()
                    }
                ]
            )
            return {
                'status': 'success',
                'message': f'Metric {metric_name} sent to CloudWatch'
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def create_alert(self, metric_name: str, condition: str, severity: str) -> Dict:
        """Create a monitoring alert."""
        alert = {
            'id': len(self.alerts) + 1,
            'metric_name': metric_name,
            'condition': condition,
            'severity': severity,
            'created_at': datetime.utcnow().isoformat(),
            'active': True
        }
        self.alerts.append(alert)
        return {
            'status': 'success',
            'alert': alert
        }

    def get_metrics_summary(self, hours: int = 1) -> Dict:
        """Get metrics summary for a time period."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_metrics = [
            m for m in self.metrics_history
            if datetime.fromisoformat(m.timestamp) > cutoff_time
        ]

        summary_by_name = {}
        for metric in recent_metrics:
            if metric.name not in summary_by_name:
                summary_by_name[metric.name] = []
            summary_by_name[metric.name].append(metric.value)

        return {
            'status': 'success',
            'period_hours': hours,
            'total_metrics': len(recent_metrics),
            'summary': {
                name: {
                    'count': len(values),
                    'avg': sum(values) / len(values),
                    'max': max(values),
                    'min': min(values)
                }
                for name, values in summary_by_name.items()
            }
        }

    def _determine_status(self, value: float, warning_threshold: float, critical_threshold: float) -> str:
        """Determine metric status based on thresholds."""
        if value >= critical_threshold:
            return MetricStatus.CRITICAL.value
        elif value >= warning_threshold:
            return MetricStatus.WARNING.value
        else:
            return MetricStatus.HEALTHY.value

    def _aggregate_status(self, statuses: List[str]) -> str:
        """Aggregate multiple statuses."""
        if MetricStatus.CRITICAL.value in statuses:
            return MetricStatus.CRITICAL.value
        elif MetricStatus.WARNING.value in statuses:
            return MetricStatus.WARNING.value
        else:
            return MetricStatus.HEALTHY.value

    def define_tools(self) -> list[dict]:
        """Define monitoring tools."""
        return [
            {
                "toolUse": {
                    "toolName": "get_cpu_metrics",
                    "description": "Get current CPU usage metrics",
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
                    "toolName": "get_memory_metrics",
                    "description": "Get current memory usage metrics",
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
                    "toolName": "get_disk_metrics",
                    "description": "Get current disk usage metrics",
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
                    "toolName": "get_system_health",
                    "description": "Get overall system health status",
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
                    "toolName": "get_process_metrics",
                    "description": "Get top processes by CPU usage",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "process_name": {
                                    "type": "string",
                                    "description": "Optional process name to filter"
                                }
                            }
                        }
                    }
                }
            },
            {
                "toolUse": {
                    "toolName": "get_metrics_summary",
                    "description": "Get metrics summary for a time period",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "hours": {
                                    "type": "integer",
                                    "description": "Number of hours to summarize"
                                }
                            }
                        }
                    }
                }
            }
        ]

    def execute_tool(self, tool_name: str, tool_input: dict) -> str:
        """Execute a monitoring tool."""
        try:
            if tool_name == "get_cpu_metrics":
                result = self.get_cpu_metrics().to_dict()
            elif tool_name == "get_memory_metrics":
                result = self.get_memory_metrics().to_dict()
            elif tool_name == "get_disk_metrics":
                result = self.get_disk_metrics().to_dict()
            elif tool_name == "get_system_health":
                result = self.get_system_health()
            elif tool_name == "get_process_metrics":
                result = self.get_process_metrics(tool_input.get("process_name"))
            elif tool_name == "get_metrics_summary":
                result = self.get_metrics_summary(tool_input.get("hours", 1))
            else:
                result = {"status": "error", "message": f"Unknown tool: {tool_name}"}

            return json.dumps(result, default=str)
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})

    def run_health_check(self, check_type: str = "full", max_iterations: int = 3) -> str:
        """Run a health check with the agent."""
        tools = self.define_tools()

        task_mapping = {
            "full": "Perform a full system health check and provide recommendations",
            "cpu": "Check CPU metrics and alert if needed",
            "memory": "Check memory usage and provide optimization suggestions",
            "processes": "List top processes by CPU usage and memory"
        }

        task = task_mapping.get(check_type, task_mapping["full"])

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": task
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

        return "Health check completed"


if __name__ == "__main__":
    print("=" * 60)
    print("System Monitoring Agent")
    print("=" * 60)

    agent = MonitoringAgent()

    print("\n1. Current System Metrics:")
    print("-" * 60)
    health = agent.get_system_health()
    print(f"Overall Health: {health['overall_health'].upper()}")
    print(f"CPU: {health['metrics']['cpu']['value']:.1f}%")
    print(f"Memory: {health['metrics']['memory']['value']:.1f}%")
    print(f"Disk: {health['metrics']['disk']['value']:.1f}%")

    print("\n2. Top Processes:")
    print("-" * 60)
    processes = agent.get_process_metrics()
    for proc in processes['processes'][:5]:
        print(f"  {proc['name']:20} - CPU: {proc['cpu_percent']:5.1f}%, Memory: {proc['memory_percent']:5.1f}%")

    print("\n3. Network Metrics:")
    print("-" * 60)
    network = agent.get_network_metrics()
    print(f"Bytes Sent: {network['bytes_sent']:,}")
    print(f"Bytes Recv: {network['bytes_recv']:,}")
    print(f"Packets Sent: {network['packets_sent']:,}")
    print(f"Packets Recv: {network['packets_recv']:,}")

    print("\n4. Alerts:")
    print("-" * 60)
    agent.create_alert("cpu_usage", "cpu > 90%", "critical")
    agent.create_alert("memory_usage", "memory > 85%", "warning")
    print(f"Total Alerts: {len(agent.alerts)}")
    for alert in agent.alerts:
        print(f"  - {alert['metric_name']}: {alert['condition']} ({alert['severity']})")

    print("\n5. Agent Health Check:")
    print("-" * 60)
    try:
        result = agent.run_health_check("cpu")
        print(f"Result:\n{result}")
    except Exception as e:
        print(f"Error: {e}")
