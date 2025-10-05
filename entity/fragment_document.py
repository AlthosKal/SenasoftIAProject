from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass, field
from bson import ObjectId


@dataclass
class FragmentDocument:
    """
    Entity representing document fragments for RAG system.
    Contains chunked content with embeddings for vector search.
    """
    id_metadata_document: str  # Reference to MetadataDocument UUID
    chunk_index: int
    content: str
    embedding: List[float]  # Vector embeddings for similarity search
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    id: Optional[str] = None
    
    def __post_init__(self):
        """Ensure timestamps are set"""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def to_dict(self) -> dict:
        """Convert entity to MongoDB document format"""
        doc = {
            "id_metadata_document": self.id_metadata_document,
            "chunk_index": self.chunk_index,
            "content": self.content,
            "embedding": self.embedding,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
        if self.id:
            doc["_id"] = ObjectId(self.id) if isinstance(self.id, str) else self.id
        return doc
    
    @classmethod
    def from_dict(cls, doc: dict) -> 'FragmentDocument':
        """Create entity from MongoDB document"""
        return cls(
            id=str(doc.get("_id")) if doc.get("_id") else None,
            id_metadata_document=doc["id_metadata_document"],
            chunk_index=doc["chunk_index"],
            content=doc["content"],
            embedding=doc["embedding"],
            created_at=doc.get("created_at", datetime.now()),
            updated_at=doc.get("updated_at", datetime.now())
        )
    
    def update_content(self, new_content: str, new_embedding: List[float]):
        """Update content and embedding"""
        self.content = new_content
        self.embedding = new_embedding
        self.updated_at = datetime.now()
    
    def get_content_preview(self, length: int = 100) -> str:
        """Get a preview of the content"""
        return self.content[:length] + "..." if len(self.content) > length else self.content