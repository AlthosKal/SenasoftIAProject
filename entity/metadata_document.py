from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from bson import ObjectId
import json


@dataclass
class MetadataDocument:
    """
    Entity representing metadata for documents in the RAG system.
    Contains document information and metadata for vector search.
    """
    document_title: str
    metadata: Dict[str, Any]
    document_type: str
    valid: bool = True
    version: int = 1
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
            "document_title": self.document_title,
            "metadata": self.metadata,
            "document_type": self.document_type,
            "valid": self.valid,
            "version": self.version,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
        if self.id:
            doc["_id"] = ObjectId(self.id) if isinstance(self.id, str) else self.id
        return doc
    
    @classmethod
    def from_dict(cls, doc: dict) -> 'MetadataDocument':
        """Create entity from MongoDB document"""
        return cls(
            id=str(doc.get("_id")) if doc.get("_id") else None,
            document_title=doc["document_title"],
            metadata=doc["metadata"],
            document_type=doc["document_type"],
            valid=doc.get("valid", True),
            version=doc.get("version", 1),
            created_at=doc.get("created_at", datetime.now()),
            updated_at=doc.get("updated_at", datetime.now())
        )
    
    def update_metadata(self, new_metadata: Dict[str, Any]):
        """Update metadata and set updated timestamp"""
        self.metadata.update(new_metadata)
        self.updated_at = datetime.now()
    
    def mark_invalid(self):
        """Mark document as invalid"""
        self.valid = False
        self.updated_at = datetime.now()
    
    def increment_version(self):
        """Increment version and update timestamp"""
        self.version += 1
        self.updated_at = datetime.now()