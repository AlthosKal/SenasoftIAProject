from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field
from bson import ObjectId


@dataclass
class ChatHistory:
    """
    Entity representing chat history for medical consultations.
    Equivalent to the Java ChatHistory entity with MongoDB compatibility.
    """
    conversation_id: str
    prompt: str
    response: str
    date: datetime = field(default_factory=datetime.now)
    id: Optional[str] = None
    
    def __post_init__(self):
        """Ensure date is set if not provided"""
        if self.date is None:
            self.date = datetime.now()
    
    def to_dict(self) -> dict:
        """Convert entity to MongoDB document format"""
        doc = {
            "conversation_id": self.conversation_id,
            "prompt": self.prompt,
            "response": self.response,
            "date": self.date
        }
        if self.id:
            doc["_id"] = ObjectId(self.id) if isinstance(self.id, str) else self.id
        return doc
    
    @classmethod
    def from_dict(cls, doc: dict) -> 'ChatHistory':
        """Create entity from MongoDB document"""
        return cls(
            id=str(doc.get("_id")) if doc.get("_id") else None,
            conversation_id=doc["conversation_id"],
            prompt=doc["prompt"],
            response=doc["response"],
            date=doc.get("date", datetime.now())
        )