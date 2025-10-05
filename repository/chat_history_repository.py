from typing import List, Optional, Dict, Any
from bson import ObjectId
from pymongo.errors import PyMongoError
from .base_repository import BaseRepository
from entity.chat_history import ChatHistory


class ChatHistoryRepository(BaseRepository):
    """
    Repository for ChatHistory entity operations.
    Handles all database interactions for chat history.
    """
    
    def __init__(self):
        super().__init__("chat_history")
    
    def find_by_id(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Find chat history by ID"""
        try:
            return self.collection.find_one({"_id": ObjectId(entity_id)})
        except (PyMongoError, ValueError) as e:
            print(f"Error finding chat history by ID {entity_id}: {e}")
            return None
    
    def save(self, entity: Dict[str, Any]) -> str:
        """Save chat history and return ID"""
        try:
            result = self.collection.insert_one(entity)
            return str(result.inserted_id)
        except PyMongoError as e:
            print(f"Error saving chat history: {e}")
            raise
    
    def update(self, entity_id: str, update_data: Dict[str, Any]) -> bool:
        """Update chat history by ID"""
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(entity_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except (PyMongoError, ValueError) as e:
            print(f"Error updating chat history {entity_id}: {e}")
            return False
    
    def delete(self, entity_id: str) -> bool:
        """Delete chat history by ID"""
        try:
            result = self.collection.delete_one({"_id": ObjectId(entity_id)})
            return result.deleted_count > 0
        except (PyMongoError, ValueError) as e:
            print(f"Error deleting chat history {entity_id}: {e}")
            return False
    
    def find_all(self, **filters) -> List[Dict[str, Any]]:
        """Find all chat histories with optional filters"""
        try:
            cursor = self.collection.find(filters).sort("date", -1)
            return list(cursor)
        except PyMongoError as e:
            print(f"Error finding chat histories: {e}")
            return []
    
    def find_by_conversation_id(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Find all chat histories for a specific conversation"""
        try:
            cursor = self.collection.find(
                {"conversation_id": conversation_id}
            ).sort("date", 1)
            return list(cursor)
        except PyMongoError as e:
            print(f"Error finding chat histories for conversation {conversation_id}: {e}")
            return []
    
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete all chat histories for a conversation"""
        try:
            result = self.collection.delete_many({"conversation_id": conversation_id})
            return result.deleted_count > 0
        except PyMongoError as e:
            print(f"Error deleting conversation {conversation_id}: {e}")
            return False
    
    def get_recent_conversations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversations"""
        try:
            pipeline = [
                {"$group": {
                    "_id": "$conversation_id",
                    "last_message": {"$last": "$prompt"},
                    "last_response": {"$last": "$response"},
                    "last_date": {"$max": "$date"},
                    "message_count": {"$sum": 1}
                }},
                {"$sort": {"last_date": -1}},
                {"$limit": limit}
            ]
            return list(self.collection.aggregate(pipeline))
        except PyMongoError as e:
            print(f"Error getting recent conversations: {e}")
            return []