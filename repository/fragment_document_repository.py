import os
from typing import List, Optional, Dict, Any
from bson import ObjectId
from pymongo.errors import PyMongoError
from .base_repository import BaseRepository


class FragmentDocumentRepository(BaseRepository):
    """
    Repository for FragmentDocument entity operations.
    Handles document fragments and vector search for RAG system.
    """
    
    def __init__(self):
        super().__init__("fragment_document")
        self._create_indexes()
    
    def _create_indexes(self):
        """Create necessary indexes including vector search index"""
        try:
            # Skip index creation if using Atlas (requires special permissions)
            if "mongodb.net" in os.getenv('DATABASE_URL', ''):
                print("MongoDB Atlas detected, skipping index creation")
                return
            
            # Index for metadata document reference
            self.collection.create_index("id_metadata_document")
            # Index for chunk ordering
            self.collection.create_index([
                ("id_metadata_document", 1),
                ("chunk_index", 1)
            ])
            # Text search index for content
            self.collection.create_index([("content", "text")])
            
            # Vector search index for MongoDB Atlas
            # This would typically be created via MongoDB Atlas UI or API
            # For local development, we'll create a regular index
            try:
                self.collection.create_index("embedding")
            except PyMongoError:
                # Embedding index might not be supported in local MongoDB
                print("Vector index for embeddings not supported in local MongoDB")
                
        except PyMongoError as e:
            print(f"Error creating indexes: {e}")
    
    def find_by_id(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Find fragment document by ID"""
        try:
            return self.collection.find_one({"_id": ObjectId(entity_id)})
        except (PyMongoError, ValueError) as e:
            print(f"Error finding fragment document by ID {entity_id}: {e}")
            return None
    
    def save(self, entity: Dict[str, Any]) -> str:
        """Save fragment document and return ID"""
        try:
            result = self.collection.insert_one(entity)
            return str(result.inserted_id)
        except PyMongoError as e:
            print(f"Error saving fragment document: {e}")
            raise
    
    def update(self, entity_id: str, update_data: Dict[str, Any]) -> bool:
        """Update fragment document by ID"""
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(entity_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except (PyMongoError, ValueError) as e:
            print(f"Error updating fragment document {entity_id}: {e}")
            return False
    
    def delete(self, entity_id: str) -> bool:
        """Delete fragment document by ID"""
        try:
            result = self.collection.delete_one({"_id": ObjectId(entity_id)})
            return result.deleted_count > 0
        except (PyMongoError, ValueError) as e:
            print(f"Error deleting fragment document {entity_id}: {e}")
            return False
    
    def find_all(self, **filters) -> List[Dict[str, Any]]:
        """Find all fragment documents with optional filters"""
        try:
            cursor = self.collection.find(filters).sort([
                ("id_metadata_document", 1),
                ("chunk_index", 1)
            ])
            return list(cursor)
        except PyMongoError as e:
            print(f"Error finding fragment documents: {e}")
            return []
    
    def find_by_metadata_document_id(self, metadata_doc_id: str) -> List[Dict[str, Any]]:
        """Find all fragments for a specific metadata document"""
        try:
            cursor = self.collection.find(
                {"id_metadata_document": metadata_doc_id}
            ).sort("chunk_index", 1)
            return list(cursor)
        except PyMongoError as e:
            print(f"Error finding fragments for metadata document {metadata_doc_id}: {e}")
            return []
    
    def delete_by_metadata_document_id(self, metadata_doc_id: str) -> bool:
        """Delete all fragments for a specific metadata document"""
        try:
            result = self.collection.delete_many({"id_metadata_document": metadata_doc_id})
            return result.deleted_count > 0
        except PyMongoError as e:
            print(f"Error deleting fragments for metadata document {metadata_doc_id}: {e}")
            return False
    
    def search_by_text(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search fragments by text content"""
        try:
            cursor = self.collection.find(
                {"$text": {"$search": query}}
            ).limit(limit)
            return list(cursor)
        except PyMongoError as e:
            print(f"Error searching fragments by text '{query}': {e}")
            return []
    
    def vector_search(self, query_embedding: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Perform vector similarity search using MongoDB Atlas Vector Search.
        For local development, this will use a basic similarity calculation.
        """
        try:
            # MongoDB Atlas vector search pipeline
            # This would work with Atlas Search index
            if self._is_atlas_available():
                pipeline = [
                    {
                        "$vectorSearch": {
                            "index": "vector_index",
                            "path": "embedding",
                            "queryVector": query_embedding,
                            "numCandidates": limit * 10,
                            "limit": limit
                        }
                    },
                    {
                        "$project": {
                            "_id": 1,
                            "id_metadata_document": 1,
                            "chunk_index": 1,
                            "content": 1,
                            "created_at": 1,
                            "score": {"$meta": "vectorSearchScore"}
                        }
                    }
                ]
                return list(self.collection.aggregate(pipeline))
            else:
                # Fallback for local development
                return self._cosine_similarity_search(query_embedding, limit)
                
        except PyMongoError as e:
            print(f"Error performing vector search: {e}")
            return []
    
    def _is_atlas_available(self) -> bool:
        """Check if running on MongoDB Atlas"""
        try:
            # Simple check for Atlas features
            server_info = self.db.client.server_info()
            return "atlas" in server_info.get("modules", [])
        except:
            return False
    
    def _cosine_similarity_search(self, query_embedding: List[float], limit: int) -> List[Dict[str, Any]]:
        """
        Fallback cosine similarity search for local development.
        This is less efficient but works without Atlas Vector Search.
        """
        try:
            # Get all documents (this is inefficient for large datasets)
            all_docs = list(self.collection.find({}))
            
            # Calculate cosine similarity for each document
            scored_docs = []
            for doc in all_docs:
                if "embedding" in doc and doc["embedding"]:
                    similarity = self._cosine_similarity(query_embedding, doc["embedding"])
                    doc["score"] = similarity
                    scored_docs.append(doc)
            
            # Sort by similarity and return top results
            scored_docs.sort(key=lambda x: x["score"], reverse=True)
            return scored_docs[:limit]
            
        except Exception as e:
            print(f"Error in fallback similarity search: {e}")
            return []
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            import math
            
            # Ensure vectors are same length
            if len(vec1) != len(vec2):
                return 0.0
            
            # Calculate dot product
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            
            # Calculate magnitudes
            magnitude1 = math.sqrt(sum(a * a for a in vec1))
            magnitude2 = math.sqrt(sum(a * a for a in vec2))
            
            # Avoid division by zero
            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0
            
            return dot_product / (magnitude1 * magnitude2)
            
        except Exception as e:
            print(f"Error calculating cosine similarity: {e}")
            return 0.0
    
    def get_fragment_stats(self) -> Dict[str, Any]:
        """Get statistics about document fragments"""
        try:
            pipeline = [
                {"$group": {
                    "_id": "$id_metadata_document",
                    "fragment_count": {"$sum": 1},
                    "total_content_length": {"$sum": {"$strLenCP": "$content"}},
                    "avg_content_length": {"$avg": {"$strLenCP": "$content"}}
                }},
                {"$group": {
                    "_id": None,
                    "total_documents": {"$sum": 1},
                    "total_fragments": {"$sum": "$fragment_count"},
                    "avg_fragments_per_doc": {"$avg": "$fragment_count"},
                    "total_content_length": {"$sum": "$total_content_length"}
                }}
            ]
            stats = list(self.collection.aggregate(pipeline))
            return stats[0] if stats else {
                "total_documents": 0,
                "total_fragments": 0,
                "avg_fragments_per_doc": 0,
                "total_content_length": 0
            }
        except PyMongoError as e:
            print(f"Error getting fragment stats: {e}")
            return {
                "total_documents": 0,
                "total_fragments": 0,
                "avg_fragments_per_doc": 0,
                "total_content_length": 0
            }