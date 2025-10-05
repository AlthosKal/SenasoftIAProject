"""
Entity layer for the medical chatbot application.
Contains all domain entities with MongoDB compatibility.
"""

from .chat_history import ChatHistory
from .metadata_document import MetadataDocument
from .fragment_document import FragmentDocument

__all__ = [
    'ChatHistory',
    'MetadataDocument', 
    'FragmentDocument'
]