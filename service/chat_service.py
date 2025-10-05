from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from entity.chat_history import ChatHistory


class ChatService(ABC):
    """
    Abstract service interface for chat operations.
    Implements Dependency Inversion Principle from SOLID.
    """
    
    @abstractmethod
    def send_text_message(self, message: str) -> Dict[str, Any]:
        """
        Process a text-only message and return response.
        
        Args:
            message: User's text message
            
        Returns:
            Dictionary containing response and conversation details
        """
        pass
    
    @abstractmethod
    def analyze_image_with_text(self, image_data: bytes, message: str) -> Dict[str, Any]:
        """
        Analyze an image with accompanying text message.
        
        Args:
            image_data: Binary image data
            message: Accompanying text message
            
        Returns:
            Dictionary containing analysis results and response
        """
        pass
    
    @abstractmethod
    def get_conversation_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve full conversation history by conversation ID.
        
        Args:
            conversation_id: Unique conversation identifier
            
        Returns:
            List of chat history entries
        """
        pass
    
    @abstractmethod
    def get_user_conversations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get list of recent conversations.
        
        Args:
            limit: Maximum number of conversations to return
            
        Returns:
            List of conversation summaries
        """
        pass
    
    @abstractmethod
    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete an entire conversation.
        
        Args:
            conversation_id: Unique conversation identifier
            
        Returns:
            True if deletion was successful, False otherwise
        """
        pass