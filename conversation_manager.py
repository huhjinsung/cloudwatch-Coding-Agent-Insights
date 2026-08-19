#!/usr/bin/env python3
"""
Conversation Manager for Multi-turn Dialogs
Manages conversation history and context for multi-turn agent interactions.
"""

import json
from datetime import datetime
from typing import List, Dict, Optional
from uuid import uuid4


class Message:
    def __init__(self, role: str, content: str, message_type: str = "text"):
        self.id = str(uuid4())
        self.role = role  # "user", "assistant", "system"
        self.content = content
        self.message_type = message_type  # "text", "tool_use", "tool_result"
        self.timestamp = datetime.utcnow().isoformat()
        self.metadata = {}

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'role': self.role,
            'content': self.content,
            'message_type': self.message_type,
            'timestamp': self.timestamp,
            'metadata': self.metadata
        }


class Conversation:
    def __init__(self, conversation_id: Optional[str] = None, title: str = ""):
        self.conversation_id = conversation_id or str(uuid4())
        self.title = title
        self.messages: List[Message] = []
        self.created_at = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()
        self.context = {}
        self.metadata = {}

    def add_message(self, role: str, content: str, message_type: str = "text") -> Message:
        """Add a message to the conversation."""
        message = Message(role, content, message_type)
        self.messages.append(message)
        self.updated_at = datetime.utcnow().isoformat()
        return message

    def get_last_message(self) -> Optional[Message]:
        """Get the last message in conversation."""
        return self.messages[-1] if self.messages else None

    def get_messages_by_role(self, role: str) -> List[Message]:
        """Get all messages from a specific role."""
        return [msg for msg in self.messages if msg.role == role]

    def get_user_messages(self) -> List[Message]:
        """Get all user messages."""
        return self.get_messages_by_role("user")

    def get_assistant_messages(self) -> List[Message]:
        """Get all assistant messages."""
        return self.get_messages_by_role("assistant")

    def get_conversation_history(self, limit: Optional[int] = None) -> List[Dict]:
        """Get conversation history."""
        messages = self.messages
        if limit:
            messages = messages[-limit:]
        return [msg.to_dict() for msg in messages]

    def get_context(self) -> Dict:
        """Get conversation context."""
        return {
            'conversation_id': self.conversation_id,
            'title': self.title,
            'message_count': len(self.messages),
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'context': self.context,
            'metadata': self.metadata
        }

    def set_context(self, key: str, value) -> None:
        """Set context variable."""
        self.context[key] = value
        self.updated_at = datetime.utcnow().isoformat()

    def get_context_value(self, key: str, default=None):
        """Get context variable."""
        return self.context.get(key, default)

    def update_metadata(self, **kwargs) -> None:
        """Update conversation metadata."""
        self.metadata.update(kwargs)
        self.updated_at = datetime.utcnow().isoformat()

    def clear_messages(self) -> None:
        """Clear all messages."""
        self.messages.clear()
        self.updated_at = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict:
        """Convert conversation to dictionary."""
        return {
            'conversation_id': self.conversation_id,
            'title': self.title,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'message_count': len(self.messages),
            'messages': [msg.to_dict() for msg in self.messages],
            'context': self.context,
            'metadata': self.metadata
        }

    def to_bedrock_format(self) -> List[Dict]:
        """Convert to Bedrock API format."""
        bedrock_messages = []
        for msg in self.messages:
            if msg.role in ["user", "assistant"]:
                bedrock_messages.append({
                    "role": msg.role,
                    "content": [{"type": "text", "text": msg.content}]
                })
        return bedrock_messages


class ConversationManager:
    """Manager for multiple conversations."""

    def __init__(self):
        self.conversations: Dict[str, Conversation] = {}
        self.active_conversation: Optional[str] = None

    def create_conversation(self, title: str = "") -> Conversation:
        """Create a new conversation."""
        conversation = Conversation(title=title)
        self.conversations[conversation.conversation_id] = conversation
        self.active_conversation = conversation.conversation_id
        return conversation

    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID."""
        return self.conversations.get(conversation_id)

    def get_active_conversation(self) -> Optional[Conversation]:
        """Get the active conversation."""
        if self.active_conversation:
            return self.conversations.get(self.active_conversation)
        return None

    def set_active_conversation(self, conversation_id: str) -> bool:
        """Set the active conversation."""
        if conversation_id in self.conversations:
            self.active_conversation = conversation_id
            return True
        return False

    def add_message_to_active(self, role: str, content: str, message_type: str = "text") -> Optional[Message]:
        """Add message to active conversation."""
        conv = self.get_active_conversation()
        if conv:
            return conv.add_message(role, content, message_type)
        return None

    def list_conversations(self) -> List[Dict]:
        """List all conversations."""
        return [
            {
                'id': conv.conversation_id,
                'title': conv.title,
                'created_at': conv.created_at,
                'message_count': len(conv.messages)
            }
            for conv in self.conversations.values()
        ]

    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation."""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            if self.active_conversation == conversation_id:
                self.active_conversation = None
            return True
        return False

    def export_conversation(self, conversation_id: str) -> Optional[Dict]:
        """Export a conversation."""
        conv = self.get_conversation(conversation_id)
        if conv:
            return conv.to_dict()
        return None

    def import_conversation(self, data: Dict) -> Conversation:
        """Import a conversation from data."""
        conv = Conversation(
            conversation_id=data.get('conversation_id'),
            title=data.get('title', '')
        )
        self.conversations[conv.conversation_id] = conv
        return conv

    def get_statistics(self) -> Dict:
        """Get manager statistics."""
        total_messages = sum(len(conv.messages) for conv in self.conversations.values())
        return {
            'total_conversations': len(self.conversations),
            'active_conversation': self.active_conversation,
            'total_messages': total_messages,
            'average_messages_per_conversation': total_messages / len(self.conversations) if self.conversations else 0
        }


if __name__ == "__main__":
    print("=" * 60)
    print("Conversation Manager")
    print("=" * 60)

    manager = ConversationManager()

    print("\n1. Create Conversations:")
    print("-" * 60)
    conv1 = manager.create_conversation("Data Analysis Discussion")
    conv2 = manager.create_conversation("AWS Resource Review")
    print(f"Created {len(manager.conversations)} conversations")

    print("\n2. Add Messages:")
    print("-" * 60)
    manager.add_message_to_active("user", "What is the total sales by region?")
    manager.add_message_to_active("assistant", "I'll analyze the sales data for you.")
    manager.add_message_to_active("user", "Thanks, can you also show trends?")
    print(f"Active conversation: {manager.active_conversation}")
    print(f"Messages: {len(manager.get_active_conversation().messages)}")

    print("\n3. Conversation History:")
    print("-" * 60)
    conv = manager.get_active_conversation()
    for msg in conv.messages:
        print(f"  [{msg.role.upper()}]: {msg.content}")

    print("\n4. Switch Conversation:")
    print("-" * 60)
    manager.set_active_conversation(conv2.conversation_id)
    manager.add_message_to_active("user", "List my EC2 instances")
    manager.add_message_to_active("assistant", "Found 3 running instances")
    print(f"Active: {manager.get_active_conversation().title}")
    print(f"Messages: {len(manager.get_active_conversation().messages)}")

    print("\n5. List All Conversations:")
    print("-" * 60)
    for conv_info in manager.list_conversations():
        print(f"  - {conv_info['title']}: {conv_info['message_count']} messages")

    print("\n6. Statistics:")
    print("-" * 60)
    stats = manager.get_statistics()
    print(f"Total Conversations: {stats['total_conversations']}")
    print(f"Total Messages: {stats['total_messages']}")
    print(f"Avg Messages/Conv: {stats['average_messages_per_conversation']:.1f}")

    print("\n7. Export Conversation:")
    print("-" * 60)
    exported = manager.export_conversation(conv1.conversation_id)
    print(f"Exported '{exported['title']}' with {len(exported['messages'])} messages")

    print("\n8. Context Management:")
    print("-" * 60)
    conv1.set_context("user_id", "user_123")
    conv1.set_context("dataset", "sales_2024")
    print(f"Context: {conv1.context}")
    print(f"Dataset: {conv1.get_context_value('dataset')}")
