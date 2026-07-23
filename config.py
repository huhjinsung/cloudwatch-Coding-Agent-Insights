#!/usr/bin/env python3
"""
Configuration file for Bedrock agents
"""

import os
from dotenv import load_dotenv

load_dotenv()

# AWS Configuration
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
AWS_PROFILE = os.getenv('AWS_PROFILE', 'default')

# Bedrock Configuration
BEDROCK_MODEL_ID = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-5-sonnet-20241022-v2:0')
BEDROCK_MAX_TOKENS = int(os.getenv('BEDROCK_MAX_TOKENS', '2048'))
BEDROCK_TEMPERATURE = float(os.getenv('BEDROCK_TEMPERATURE', '0.7'))

# Agent Configuration
MAX_ITERATIONS = int(os.getenv('MAX_ITERATIONS', '5'))
AGENT_TIMEOUT = int(os.getenv('AGENT_TIMEOUT', '30'))

# Web Server Configuration
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.getenv('FLASK_PORT', '5000'))
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'bedrock_agents.log')

# Model Configurations
AVAILABLE_MODELS = {
    'claude-opus': 'anthropic.claude-3-opus-20250219-v1:0',
    'claude-sonnet': 'anthropic.claude-3-5-sonnet-20241022-v2:0',
    'claude-haiku': 'anthropic.claude-3-haiku-20250307-v1:0'
}

# Agent Specifications
AGENT_SPECS = {
    'data_analyzer': {
        'model': AVAILABLE_MODELS['claude-sonnet'],
        'max_tokens': 2048,
        'temperature': 0.5
    },
    'code_assistant': {
        'model': AVAILABLE_MODELS['claude-opus'],
        'max_tokens': 4096,
        'temperature': 0.7
    },
    'general_assistant': {
        'model': AVAILABLE_MODELS['claude-sonnet'],
        'max_tokens': 2048,
        'temperature': 0.7
    }
}

# Data Analysis Settings
DATA_SAMPLE_SIZE = int(os.getenv('DATA_SAMPLE_SIZE', '365'))
DATA_CACHE_ENABLED = os.getenv('DATA_CACHE_ENABLED', 'True').lower() == 'true'

# AWS Service Settings
S3_BUCKET_PREFIX = os.getenv('S3_BUCKET_PREFIX', '')
EC2_INSTANCE_FILTERS = {
    'running': [{'Name': 'instance-state-name', 'Values': ['running']}],
    'all': []
}

# API Rate Limiting
RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'False').lower() == 'true'
RATE_LIMIT_REQUESTS = int(os.getenv('RATE_LIMIT_REQUESTS', '100'))
RATE_LIMIT_PERIOD = int(os.getenv('RATE_LIMIT_PERIOD', '60'))

# Security Settings
CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
API_KEY_REQUIRED = os.getenv('API_KEY_REQUIRED', 'False').lower() == 'true'
API_KEY = os.getenv('API_KEY', '')
