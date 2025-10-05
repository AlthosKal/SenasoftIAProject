"""
Service layer for the medical chatbot application.
Contains business logic and orchestrates between repositories and external services.
"""

from .chat_service import ChatService
from .chat_service_impl import ChatServiceImpl

__all__ = [
    'ChatService',
    'ChatServiceImpl'
]