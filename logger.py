#!/usr/bin/env python3
"""
Logging Module for Bedrock Agents
Provides centralized logging for all agent activities.
"""

import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path


class AgentLogger:
    """Centralized logging for Bedrock agents."""

    def __init__(self, log_file: str = "bedrock_agents.log", log_level: str = "INFO"):
        self.log_file = log_file
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Setup logger with file and console handlers."""
        logger = logging.getLogger('bedrock_agent')
        logger.setLevel(self.log_level)

        # Create logs directory if it doesn't exist
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)

        log_path = log_dir / self.log_file

        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(self.log_level)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    def info(self, message: str, **kwargs):
        """Log info level message."""
        self.logger.info(message, **kwargs)

    def debug(self, message: str, **kwargs):
        """Log debug level message."""
        self.logger.debug(message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning level message."""
        self.logger.warning(message, **kwargs)

    def error(self, message: str, **kwargs):
        """Log error level message."""
        self.logger.error(message, **kwargs)

    def critical(self, message: str, **kwargs):
        """Log critical level message."""
        self.logger.critical(message, **kwargs)

    def log_agent_invocation(self, agent_name: str, input_data: dict):
        """Log agent invocation."""
        self.info(f"Agent '{agent_name}' invoked with input: {input_data}")

    def log_agent_response(self, agent_name: str, response_summary: str, duration: float):
        """Log agent response."""
        self.info(f"Agent '{agent_name}' completed in {duration:.2f}s - {response_summary}")

    def log_tool_usage(self, agent_name: str, tool_name: str, tool_input: dict):
        """Log tool usage."""
        self.debug(f"Agent '{agent_name}' using tool '{tool_name}' with input: {tool_input}")

    def log_tool_result(self, agent_name: str, tool_name: str, result: str):
        """Log tool result."""
        self.debug(f"Agent '{agent_name}' tool '{tool_name}' result: {result[:100]}...")

    def log_error_with_context(self, agent_name: str, error: Exception, context: str = ""):
        """Log error with context."""
        self.error(f"Agent '{agent_name}' error: {str(error)} | Context: {context}")

    def log_api_request(self, endpoint: str, method: str, status_code: int, duration: float):
        """Log API request."""
        self.info(f"API {method} {endpoint} - Status: {status_code} - Duration: {duration:.3f}s")

    def log_data_analysis(self, dataset_name: str, operation: str, result_summary: str):
        """Log data analysis operation."""
        self.info(f"Data Analysis: {operation} on '{dataset_name}' - {result_summary}")

    def log_aws_service_call(self, service_name: str, operation: str, result: str):
        """Log AWS service call."""
        self.debug(f"AWS {service_name}: {operation} - {result}")


# Global logger instance
_agent_logger = None


def get_logger(log_file: str = "bedrock_agents.log", log_level: str = "INFO") -> AgentLogger:
    """Get or create global logger instance."""
    global _agent_logger
    if _agent_logger is None:
        _agent_logger = AgentLogger(log_file, log_level)
    return _agent_logger


if __name__ == "__main__":
    print("=" * 60)
    print("Bedrock Agent Logger")
    print("=" * 60)

    logger = get_logger(log_level="DEBUG")

    print("\n1. Basic Logging:")
    print("-" * 60)
    logger.info("This is an info message")
    logger.debug("This is a debug message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")

    print("\n2. Agent Logging:")
    print("-" * 60)
    logger.log_agent_invocation("DataAnalyzer", {"dataset": "sales", "query": "total by region"})
    logger.log_agent_response("DataAnalyzer", "Found 4 regions with total sales", 1.234)

    print("\n3. Tool Logging:")
    print("-" * 60)
    logger.log_tool_usage("DataAnalyzer", "filter_data", {"column": "region", "value": "North"})
    logger.log_tool_result("DataAnalyzer", "filter_data", '{"rows_found": 91, "status": "success"}')

    print("\n4. API Logging:")
    print("-" * 60)
    logger.log_api_request("/chat", "POST", 200, 0.456)
    logger.log_api_request("/agents", "GET", 200, 0.012)
    logger.log_api_request("/analyze", "POST", 400, 0.001)

    print("\n5. Data Analysis Logging:")
    print("-" * 60)
    logger.log_data_analysis("weather", "correlation", "Found correlation: temp vs humidity")

    print("\n6. AWS Service Logging:")
    print("-" * 60)
    logger.log_aws_service_call("S3", "list_buckets", "Found 3 buckets")
    logger.log_aws_service_call("EC2", "describe_instances", "Found 2 running instances")

    print("\n7. Error Logging:")
    print("-" * 60)
    try:
        raise ValueError("Test error for logging")
    except Exception as e:
        logger.log_error_with_context("TestAgent", e, "During initialization")

    print("\n✓ Log file created in 'logs/bedrock_agents.log'")
