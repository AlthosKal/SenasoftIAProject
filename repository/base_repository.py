from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
import os


class BaseRepository(ABC):
    """
    Abstract base repository implementing common database operations.
    Follows Repository pattern for SOLID principles.
    """
    
    def __init__(self, collection_name: str):
        self.client: MongoClient = self._get_mongo_client()
        self.db: Database = self.client.get_database("medico_ia")  # Nombre fijo de la base de datos
        self.collection: Collection = self.db[collection_name]
    
    def _get_mongo_client(self) -> MongoClient:
        """Get MongoDB client from environment variables"""
        mongo_uri = os.getenv('DATABASE_URL')
        if not mongo_uri:
            raise ValueError("DATABASE_URL environment variable not found. Please check your .env file.")
        
        print(f"Connecting to MongoDB: {mongo_uri[:20]}..." if len(mongo_uri) > 20 else mongo_uri)
        return MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    
    @abstractmethod
    def find_by_id(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Find entity by ID"""
        pass
    
    @abstractmethod
    def save(self, entity: Dict[str, Any]) -> str:
        """Save entity and return ID"""
        pass
    
    @abstractmethod
    def update(self, entity_id: str, update_data: Dict[str, Any]) -> bool:
        """Update entity by ID"""
        pass
    
    @abstractmethod
    def delete(self, entity_id: str) -> bool:
        """Delete entity by ID"""
        pass
    
    @abstractmethod
    def find_all(self, **filters) -> List[Dict[str, Any]]:
        """Find all entities with optional filters"""
        pass
    
    def close_connection(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()