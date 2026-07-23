#!/usr/bin/env python3
"""
Test suite for Bedrock agents
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json


class TestDataAnalysisAgent(unittest.TestCase):
    """Test cases for DataAnalysisAgent"""

    def setUp(self):
        """Set up test fixtures."""
        from data_analysis_agent import DataAnalysisAgent
        self.agent = DataAnalysisAgent()
        self.agent.load_sample_data()

    def test_load_sample_data(self):
        """Test that sample data is loaded correctly."""
        self.assertIn('sales', self.agent.data_store)
        self.assertIn('weather', self.agent.data_store)
        self.assertGreater(len(self.agent.data_store['sales']), 0)

    def test_get_data_summary(self):
        """Test getting data summary."""
        summary = self.agent.get_data_summary('sales')
        self.assertEqual(summary['dataset_name'], 'sales')
        self.assertIn('shape', summary)
        self.assertIn('columns', summary)

    def test_get_data_summary_nonexistent(self):
        """Test getting summary for non-existent dataset."""
        summary = self.agent.get_data_summary('nonexistent')
        self.assertIn('error', summary)

    def test_filter_data_equals(self):
        """Test filtering data with equals operation."""
        result = self.agent.filter_data('sales', 'region', 'North', 'equals')
        self.assertEqual(result['filter_applied']['operation'], 'equals')
        self.assertGreater(result['rows_found'], 0)

    def test_filter_data_greater_than(self):
        """Test filtering data with greater_than operation."""
        result = self.agent.filter_data('sales', 'sales', 10100, 'greater_than')
        self.assertEqual(result['filter_applied']['operation'], 'greater_than')

    def test_calculate_correlation(self):
        """Test correlation calculation."""
        result = self.agent.calculate_correlation('sales')
        self.assertEqual(result['dataset'], 'sales')
        self.assertIn('correlation_matrix', result)

    def test_aggregate_data_sum(self):
        """Test data aggregation with sum."""
        result = self.agent.aggregate_data('sales', 'region', 'sum', 'sales')
        self.assertIn('results', result)
        self.assertGreater(len(result['results']), 0)

    def test_aggregate_data_mean(self):
        """Test data aggregation with mean."""
        result = self.agent.aggregate_data('sales', 'region', 'mean', 'sales')
        self.assertIn('results', result)

    def test_define_tools(self):
        """Test tool definitions."""
        tools = self.agent.define_tools()
        tool_names = [t['toolUse']['toolName'] for t in tools]
        self.assertIn('get_data_summary', tool_names)
        self.assertIn('filter_data', tool_names)
        self.assertIn('calculate_correlation', tool_names)


class TestAWSServiceAgent(unittest.TestCase):
    """Test cases for AWSServiceAgent"""

    def setUp(self):
        """Set up test fixtures."""
        from aws_service_agent import AWSServiceAgent
        self.agent = AWSServiceAgent()

    @patch('boto3.client')
    def test_list_s3_buckets(self, mock_boto):
        """Test listing S3 buckets."""
        mock_s3 = MagicMock()
        mock_boto.return_value = mock_s3

        self.agent.s3_client = mock_s3
        mock_s3.list_buckets.return_value = {
            'Buckets': [
                {'Name': 'bucket1', 'CreationDate': '2024-01-01'},
                {'Name': 'bucket2', 'CreationDate': '2024-01-02'}
            ]
        }

        result = self.agent.list_s3_buckets()
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['bucket_count'], 2)

    def test_define_tools(self):
        """Test tool definitions."""
        tools = self.agent.define_tools()
        tool_names = [t['toolUse']['toolName'] for t in tools]
        self.assertIn('list_s3_buckets', tool_names)
        self.assertIn('list_ec2_instances', tool_names)
        self.assertIn('get_cloudwatch_metrics', tool_names)

    def test_execute_tool_unknown(self):
        """Test executing unknown tool."""
        result = self.agent.execute_tool('unknown_tool', {})
        parsed = json.loads(result)
        self.assertIn('error', parsed)


class TestWebServerAgent(unittest.TestCase):
    """Test cases for Web Server Agent"""

    def setUp(self):
        """Set up test fixtures."""
        from web_server_agent import app
        self.app = app
        self.client = app.test_client()

    def test_health_check(self):
        """Test health check endpoint."""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')

    def test_list_agents(self):
        """Test listing agents."""
        response = self.client.get('/agents')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertGreater(data['count'], 0)

    def test_get_agent_info(self):
        """Test getting agent info."""
        response = self.client.get('/agents/assistant')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['id'], 'assistant')

    def test_get_agent_info_nonexistent(self):
        """Test getting info for non-existent agent."""
        response = self.client.get('/agents/nonexistent')
        self.assertEqual(response.status_code, 404)

    def test_chat_missing_message(self):
        """Test chat with missing message."""
        response = self.client.post(
            '/chat',
            data=json.dumps({'agent_id': 'assistant'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_analyze_missing_text(self):
        """Test analyze with missing text."""
        response = self.client.post(
            '/analyze',
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_batch_process_invalid_messages(self):
        """Test batch processing with invalid messages."""
        response = self.client.post(
            '/batch',
            data=json.dumps({'messages': 'not a list'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_not_found(self):
        """Test 404 error handling."""
        response = self.client.get('/nonexistent-endpoint')
        self.assertEqual(response.status_code, 404)


class TestIntegration(unittest.TestCase):
    """Integration tests"""

    def test_data_analysis_workflow(self):
        """Test complete data analysis workflow."""
        from data_analysis_agent import DataAnalysisAgent

        agent = DataAnalysisAgent()
        agent.load_sample_data()

        # Get summary
        summary = agent.get_data_summary('sales')
        self.assertEqual(summary['dataset_name'], 'sales')

        # Filter data
        filtered = agent.filter_data('sales', 'region', 'North')
        self.assertGreater(filtered['rows_found'], 0)

        # Aggregate data
        aggregated = agent.aggregate_data('sales', 'region', 'sum', 'sales')
        self.assertIn('results', aggregated)

    def test_tools_schema_validity(self):
        """Test that all tools have valid schemas."""
        from data_analysis_agent import DataAnalysisAgent
        from aws_service_agent import AWSServiceAgent

        for agent_class in [DataAnalysisAgent, AWSServiceAgent]:
            agent = agent_class()
            tools = agent.define_tools()

            for tool in tools:
                self.assertIn('toolUse', tool)
                tool_use = tool['toolUse']
                self.assertIn('toolName', tool_use)
                self.assertIn('description', tool_use)
                self.assertIn('inputSchema', tool_use)
                self.assertIn('json', tool_use['inputSchema'])


if __name__ == '__main__':
    unittest.main()
