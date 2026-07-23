#!/usr/bin/env python3
"""
Notification & Email Agent
An agent that can send notifications, manage alerts, and handle communications.
"""

import json
import boto3
from datetime import datetime
from typing import Optional, List
from enum import Enum


class NotificationType(Enum):
    EMAIL = "email"
    SMS = "sms"
    SLACK = "slack"
    ALERT = "alert"


class NotificationAgent:
    def __init__(self, region_name: str = "us-east-1"):
        self.bedrock_client = boto3.client('bedrock-runtime', region_name=region_name)
        self.ses_client = boto3.client('ses', region_name=region_name)
        self.sns_client = boto3.client('sns', region_name=region_name)
        self.region = region_name
        self.notification_history = []
        self.alert_rules = {}

    def send_email(self, recipient: str, subject: str, body: str, sender: str = "noreply@example.com") -> dict:
        """Send an email using SES."""
        try:
            response = self.ses_client.send_email(
                Source=sender,
                Destination={'ToAddresses': [recipient]},
                Message={
                    'Subject': {'Data': subject},
                    'Body': {'Text': {'Data': body}}
                }
            )

            notification = {
                "type": "email",
                "recipient": recipient,
                "subject": subject,
                "status": "sent",
                "message_id": response.get('MessageId'),
                "timestamp": datetime.utcnow().isoformat()
            }
            self.notification_history.append(notification)

            return {
                "status": "success",
                "message_id": response.get('MessageId'),
                "notification": notification
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def send_sms(self, phone_number: str, message: str) -> dict:
        """Send an SMS using SNS."""
        try:
            response = self.sns_client.publish(
                PhoneNumber=phone_number,
                Message=message,
                MessageAttributes={
                    'AWS.SNS.SMS.SenderID': {'DataType': 'String', 'StringValue': 'Agent'},
                    'AWS.SNS.SMS.SMSType': {'DataType': 'String', 'StringValue': 'Transactional'}
                }
            )

            notification = {
                "type": "sms",
                "phone_number": phone_number,
                "message": message,
                "status": "sent",
                "message_id": response.get('MessageId'),
                "timestamp": datetime.utcnow().isoformat()
            }
            self.notification_history.append(notification)

            return {
                "status": "success",
                "message_id": response.get('MessageId'),
                "notification": notification
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def create_sns_topic(self, topic_name: str) -> dict:
        """Create an SNS topic for subscriptions."""
        try:
            response = self.sns_client.create_topic(Name=topic_name)
            return {
                "status": "success",
                "topic_arn": response.get('TopicArn'),
                "topic_name": topic_name
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def publish_to_topic(self, topic_arn: str, message: str, subject: str = "Notification") -> dict:
        """Publish a message to an SNS topic."""
        try:
            response = self.sns_client.publish(
                TopicArn=topic_arn,
                Message=message,
                Subject=subject
            )

            notification = {
                "type": "topic",
                "topic_arn": topic_arn,
                "message": message,
                "status": "published",
                "message_id": response.get('MessageId'),
                "timestamp": datetime.utcnow().isoformat()
            }
            self.notification_history.append(notification)

            return {
                "status": "success",
                "message_id": response.get('MessageId'),
                "notification": notification
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def list_verified_emails(self) -> dict:
        """List verified email addresses in SES."""
        try:
            response = self.ses_client.list_verified_email_addresses()
            emails = response.get('VerifiedEmailAddresses', [])
            return {
                "status": "success",
                "verified_emails": emails,
                "count": len(emails)
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_sns_topics(self) -> dict:
        """List all SNS topics."""
        try:
            response = self.sns_client.list_topics()
            topics = [{'arn': t['TopicArn']} for t in response.get('Topics', [])]
            return {
                "status": "success",
                "topics": topics,
                "count": len(topics)
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def add_alert_rule(self, rule_name: str, condition: str, action: str, notification_type: str) -> dict:
        """Add an alert rule."""
        rule = {
            "name": rule_name,
            "condition": condition,
            "action": action,
            "notification_type": notification_type,
            "created_at": datetime.utcnow().isoformat(),
            "enabled": True
        }
        self.alert_rules[rule_name] = rule
        return {
            "status": "success",
            "rule_name": rule_name,
            "rule": rule
        }

    def list_alert_rules(self) -> dict:
        """List all alert rules."""
        return {
            "status": "success",
            "rules": self.alert_rules,
            "count": len(self.alert_rules)
        }

    def trigger_alert(self, rule_name: str, details: str) -> dict:
        """Trigger an alert based on a rule."""
        if rule_name not in self.alert_rules:
            return {"status": "error", "message": f"Rule '{rule_name}' not found"}

        rule = self.alert_rules[rule_name]
        alert = {
            "rule_name": rule_name,
            "notification_type": rule["notification_type"],
            "action": rule["action"],
            "details": details,
            "triggered_at": datetime.utcnow().isoformat(),
            "status": "triggered"
        }
        self.notification_history.append(alert)

        return {
            "status": "success",
            "alert": alert,
            "rule": rule
        }

    def get_notification_history(self, limit: int = 10) -> dict:
        """Get notification history."""
        recent = self.notification_history[-limit:]
        return {
            "status": "success",
            "total": len(self.notification_history),
            "recent": recent,
            "limit": limit
        }

    def generate_email_from_template(self, template_type: str, data: dict) -> dict:
        """Generate email content from a template."""
        templates = {
            "welcome": {
                "subject": "Welcome!",
                "body_template": "Welcome {name}! Thank you for joining us. Your account is ready to use."
            },
            "alert": {
                "subject": "Alert: {alert_type}",
                "body_template": "Alert: {alert_type}\nDetails: {details}\nTime: {timestamp}"
            },
            "report": {
                "subject": "Daily Report",
                "body_template": "Daily Report\n\n{content}\n\nGenerated: {timestamp}"
            },
            "confirmation": {
                "subject": "Action Confirmation",
                "body_template": "Your action has been confirmed:\n{action}\n\nTimestamp: {timestamp}"
            }
        }

        if template_type not in templates:
            return {"status": "error", "message": f"Template '{template_type}' not found"}

        template = templates[template_type]
        data['timestamp'] = datetime.utcnow().isoformat()

        try:
            subject = template['subject'].format(**data)
            body = template['body_template'].format(**data)
            return {
                "status": "success",
                "template_type": template_type,
                "subject": subject,
                "body": body
            }
        except KeyError as e:
            return {"status": "error", "message": f"Missing template variable: {e}"}

    def define_tools(self) -> list[dict]:
        """Define tools for notification operations."""
        return [
            {
                "toolUse": {
                    "toolName": "send_email",
                    "description": "Send an email using AWS SES",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "recipient": {
                                    "type": "string",
                                    "description": "Email recipient address"
                                },
                                "subject": {
                                    "type": "string",
                                    "description": "Email subject"
                                },
                                "body": {
                                    "type": "string",
                                    "description": "Email body content"
                                },
                                "sender": {
                                    "type": "string",
                                    "description": "Sender email address"
                                }
                            },
                            "required": ["recipient", "subject", "body"]
                        }
                    }
                }
            },
            {
                "toolUse": {
                    "toolName": "send_sms",
                    "description": "Send an SMS using AWS SNS",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "phone_number": {
                                    "type": "string",
                                    "description": "Phone number with country code"
                                },
                                "message": {
                                    "type": "string",
                                    "description": "SMS message content"
                                }
                            },
                            "required": ["phone_number", "message"]
                        }
                    }
                }
            },
            {
                "toolUse": {
                    "toolName": "create_sns_topic",
                    "description": "Create an SNS topic for notifications",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "topic_name": {
                                    "type": "string",
                                    "description": "Name of the SNS topic"
                                }
                            },
                            "required": ["topic_name"]
                        }
                    }
                }
            },
            {
                "toolUse": {
                    "toolName": "add_alert_rule",
                    "description": "Add an alert rule",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "rule_name": {
                                    "type": "string",
                                    "description": "Name of the alert rule"
                                },
                                "condition": {
                                    "type": "string",
                                    "description": "Condition for triggering alert"
                                },
                                "action": {
                                    "type": "string",
                                    "description": "Action to take when triggered"
                                },
                                "notification_type": {
                                    "type": "string",
                                    "description": "Type of notification (email, sms, slack)"
                                }
                            },
                            "required": ["rule_name", "condition", "action", "notification_type"]
                        }
                    }
                }
            },
            {
                "toolUse": {
                    "toolName": "list_alert_rules",
                    "description": "List all alert rules",
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
                    "toolName": "get_notification_history",
                    "description": "Get notification history",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "limit": {
                                    "type": "integer",
                                    "description": "Number of recent notifications to retrieve"
                                }
                            }
                        }
                    }
                }
            },
            {
                "toolUse": {
                    "toolName": "generate_email_from_template",
                    "description": "Generate email from a template",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "template_type": {
                                    "type": "string",
                                    "description": "Template type (welcome, alert, report, confirmation)"
                                },
                                "data": {
                                    "type": "object",
                                    "description": "Data to fill the template"
                                }
                            },
                            "required": ["template_type", "data"]
                        }
                    }
                }
            }
        ]

    def execute_tool(self, tool_name: str, tool_input: dict) -> str:
        """Execute a tool and return the result."""
        try:
            if tool_name == "send_email":
                result = self.send_email(
                    tool_input.get("recipient", ""),
                    tool_input.get("subject", ""),
                    tool_input.get("body", ""),
                    tool_input.get("sender", "noreply@example.com")
                )
            elif tool_name == "send_sms":
                result = self.send_sms(
                    tool_input.get("phone_number", ""),
                    tool_input.get("message", "")
                )
            elif tool_name == "create_sns_topic":
                result = self.create_sns_topic(tool_input.get("topic_name", ""))
            elif tool_name == "add_alert_rule":
                result = self.add_alert_rule(
                    tool_input.get("rule_name", ""),
                    tool_input.get("condition", ""),
                    tool_input.get("action", ""),
                    tool_input.get("notification_type", "")
                )
            elif tool_name == "list_alert_rules":
                result = self.list_alert_rules()
            elif tool_name == "get_notification_history":
                result = self.get_notification_history(tool_input.get("limit", 10))
            elif tool_name == "generate_email_from_template":
                result = self.generate_email_from_template(
                    tool_input.get("template_type", ""),
                    tool_input.get("data", {})
                )
            else:
                result = {"status": "error", "message": f"Unknown tool: {tool_name}"}

            return json.dumps(result, default=str)
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})

    def run_notification_task(self, task: str, max_iterations: int = 5) -> str:
        """Run a notification task with the agent."""
        tools = self.define_tools()
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

        return "Max iterations reached"


if __name__ == "__main__":
    print("=" * 60)
    print("Notification & Email Agent")
    print("=" * 60)

    agent = NotificationAgent()

    print("\n1. Available Alert Rules:")
    print("-" * 60)
    try:
        # Add some sample alert rules
        agent.add_alert_rule(
            "high_cpu",
            "CPU usage > 80%",
            "Send email notification",
            "email"
        )
        agent.add_alert_rule(
            "disk_full",
            "Disk usage > 90%",
            "Send SMS alert",
            "sms"
        )
        rules = agent.list_alert_rules()
        print(f"Total rules: {rules['count']}")
        for name, rule in rules['rules'].items():
            print(f"  - {name}: {rule['condition']} -> {rule['action']}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n2. Email Template Generation:")
    print("-" * 60)
    try:
        email = agent.generate_email_from_template(
            "alert",
            {"alert_type": "High CPU Usage", "details": "CPU reached 95%"}
        )
        print(f"Subject: {email['subject']}")
        print(f"Body:\n{email['body']}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n3. Notification History:")
    print("-" * 60)
    try:
        history = agent.get_notification_history(limit=5)
        print(f"Total notifications: {history['total']}")
        print(f"Recent: {len(history['recent'])} items")
    except Exception as e:
        print(f"Error: {e}")

    print("\n4. Agent Task Example:")
    print("-" * 60)
    task = "Create an alert rule for when database connections exceed 100, and generate a welcome email template"
    try:
        result = agent.run_notification_task(task)
        print(f"Result:\n{result}")
    except Exception as e:
        print(f"Error: {e}")
