import os
from typing import List, Optional, Dict, Any
from bson import ObjectId
from pymongo.errors import PyMongoError
from .base_repository import BaseRepository


class MetadataDocumentRepository(BaseRepository):
    """
    Repository for MetadataDocument entity operations.
    Handles document metadata for RAG system.
    """
    
    def __init__(self):
        super().__init__("metadata_document")
        self._create_indexes()
    
    def _create_indexes(self):
        """Create necessary indexes for optimal performance"""
        try:
            # Skip index creation if using Atlas (requires special permissions)
            database_url = os.getenv('DATABASE_URL', '')
            if "mongodb.net" in database_url or "mongodb+srv" in database_url:
                print("MongoDB Atlas detected, skipping index creation")
                return
                
            # Index for document title search
            self.collection.create_index("document_title")
            # Index for document type filtering
            self.collection.create_index("document_type")
            # Index for validity filtering
            self.collection.create_index("valid")
            # Compound index for efficient queries
            self.collection.create_index([
                ("document_type", 1),
                ("valid", 1),
                ("created_at", -1)
            ])
        except PyMongoError as e:
            print(f"Error creating indexes: {e}")
    
    def find_by_id(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Find metadata document by ID"""
        try:
            return self.collection.find_one({"_id": ObjectId(entity_id)})
        except (PyMongoError, ValueError) as e:
            print(f"Error finding metadata document by ID {entity_id}: {e}")
            return None
    
    def save(self, entity: Dict[str, Any]) -> str:
        """Save metadata document and return ID"""
        try:
            result = self.collection.insert_one(entity)
            return str(result.inserted_id)
        except PyMongoError as e:
            print(f"Error saving metadata document: {e}")
            raise
    
    def update(self, entity_id: str, update_data: Dict[str, Any]) -> bool:
        """Update metadata document by ID"""
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(entity_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except (PyMongoError, ValueError) as e:
            print(f"Error updating metadata document {entity_id}: {e}")
            return False
    
    def delete(self, entity_id: str) -> bool:
        """Delete metadata document by ID"""
        try:
            result = self.collection.delete_one({"_id": ObjectId(entity_id)})
            return result.deleted_count > 0
        except (PyMongoError, ValueError) as e:
            print(f"Error deleting metadata document {entity_id}: {e}")
            return False
    
    def find_all(self, **filters) -> List[Dict[str, Any]]:
        """Find all metadata documents with optional filters"""
        try:
            # Default to only valid documents
            if "valid" not in filters:
                filters["valid"] = True
            
            cursor = self.collection.find(filters).sort("created_at", -1)
            return list(cursor)
        except PyMongoError as e:
            print(f"Error finding metadata documents: {e}")
            return []
    
    def find_by_document_type(self, document_type: str) -> List[Dict[str, Any]]:
        """Find metadata documents by type"""
        return self.find_all(document_type=document_type)
    
    def find_by_title_pattern(self, pattern: str) -> List[Dict[str, Any]]:
        """Find metadata documents by title pattern"""
        try:
            cursor = self.collection.find({
                "document_title": {"$regex": pattern, "$options": "i"},
                "valid": True
            }).sort("created_at", -1)
            return list(cursor)
        except PyMongoError as e:
            print(f"Error finding documents by title pattern {pattern}: {e}")
            return []
    
    def mark_as_invalid(self, entity_id: str) -> bool:
        """Mark document as invalid (soft delete)"""
        return self.update(entity_id, {"valid": False, "updated_at": None})
    
    def get_document_stats(self) -> Dict[str, Any]:
        """Get statistics about documents"""
        try:
            pipeline = [
                {"$group": {
                    "_id": "$document_type",
                    "count": {"$sum": 1},
                    "valid_count": {"$sum": {"$cond": ["$valid", 1, 0]}},
                    "invalid_count": {"$sum": {"$cond": ["$valid", 0, 1]}}
                }},
                {"$sort": {"count": -1}}
            ]
            stats = list(self.collection.aggregate(pipeline))
            
            # Get total count
            total_pipeline = [
                {"$group": {
                    "_id": None,
                    "total": {"$sum": 1},
                    "valid_total": {"$sum": {"$cond": ["$valid", 1, 0]}},
                    "invalid_total": {"$sum": {"$cond": ["$valid", 0, 1]}}
                }}
            ]
            total_stats = list(self.collection.aggregate(total_pipeline))
            
            return {
                "by_type": stats,
                "total": total_stats[0] if total_stats else {"total": 0, "valid_total": 0, "invalid_total": 0}
            }
        except PyMongoError as e:
            print(f"Error getting document stats: {e}")
            return {"by_type": [], "total": {"total": 0, "valid_total": 0, "invalid_total": 0}}
    
    def find_by_document_id(self, document_id: str) -> List[Dict[str, Any]]:
        """Find metadata documents by document_id"""
        try:
            cursor = self.collection.find({"document_id": document_id})
            return list(cursor)
        except PyMongoError as e:
            print(f"Error finding documents by document_id {document_id}: {e}")
            return []