import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
import base64
import io
from PIL import Image

from .chat_service import ChatService
from repository.chat_history_repository import ChatHistoryRepository
from repository.fragment_document_repository import FragmentDocumentRepository
from entity.chat_history import ChatHistory


class ChatServiceImpl(ChatService):
    """
    Implementation of ChatService interface.
    Handles all chat-related business logic with RAG and LLM integration.
    """
    
    def __init__(self):
        self.chat_repository = ChatHistoryRepository()
        self.fragment_repository = FragmentDocumentRepository()
        self.llm_service = None  # Will be initialized with LangChain
        self.rag_service = None  # Will be initialized with RAG system
        
    def send_text_message(self, message: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """Process a text-only message using RAG and LLM"""
        try:
            # Generate or use existing conversation ID
            if not conversation_id:
                conversation_id = self._generate_conversation_id()
            
            # Retrieve relevant context using RAG
            context = self._get_rag_context(message)
            
            # Generate response using LLM with context
            response = self._generate_llm_response(message, context)
            
            # Save to chat history
            chat_entry = ChatHistory(
                conversation_id=conversation_id,
                prompt=message,
                response=response["content"]
            )
            
            chat_id = self.chat_repository.save(chat_entry.to_dict())
            
            return {
                "conversation_id": conversation_id,
                "response": response["content"],
                "confidence": response.get("confidence", 0.8),
                "sources": context.get("sources", []),
                "chat_id": chat_id,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error processing text message: {e}")
            return {
                "error": "Error processing message",
                "message": str(e)
            }
    
    def analyze_image_with_text(self, image_data: bytes, message: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """Analyze medical image with accompanying text using multimodal LLM"""
        try:
            # Generate or use existing conversation ID
            if not conversation_id:
                conversation_id = self._generate_conversation_id()
            
            # Process and validate image
            processed_image = self._process_medical_image(image_data)
            if not processed_image:
                return {"error": "Invalid or unsupported image format"}
            
            # Get RAG context for text portion
            text_context = self._get_rag_context(message)
            
            # Analyze image using multimodal LLM (LLaVA)
            image_analysis = self._analyze_image_with_llm(processed_image, message, text_context)
            
            # Combine text and image analysis
            combined_response = self._combine_text_image_analysis(message, image_analysis, text_context)
            
            # Save to chat history
            chat_entry = ChatHistory(
                conversation_id=conversation_id,
                prompt=f"[IMAGE] {message}",
                response=combined_response["content"]
            )
            
            chat_id = self.chat_repository.save(chat_entry.to_dict())
            
            return {
                "conversation_id": conversation_id,
                "response": combined_response["content"],
                "image_analysis": image_analysis,
                "confidence": combined_response.get("confidence", 0.8),
                "sources": text_context.get("sources", []),
                "chat_id": chat_id,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error analyzing image with text: {e}")
            return {
                "error": "Error analyzing image",
                "message": str(e)
            }
    
    def get_conversation_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Retrieve full conversation history"""
        try:
            history_docs = self.chat_repository.find_by_conversation_id(conversation_id)
            
            history = []
            for doc in history_docs:
                chat_entry = ChatHistory.from_dict(doc)
                history.append({
                    "id": chat_entry.id,
                    "prompt": chat_entry.prompt,
                    "response": chat_entry.response,
                    "date": chat_entry.date.isoformat()
                })
            
            return history
            
        except Exception as e:
            print(f"Error retrieving conversation history: {e}")
            return []
    
    def get_user_conversations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversations"""
        try:
            conversations = self.chat_repository.get_recent_conversations(limit)
            
            formatted_conversations = []
            for conv in conversations:
                formatted_conversations.append({
                    "conversation_id": conv["_id"],
                    "last_message": conv.get("last_message", ""),
                    "last_response": conv.get("last_response", ""),
                    "last_date": conv.get("last_date").isoformat() if conv.get("last_date") else "",
                    "message_count": conv.get("message_count", 0)
                })
            
            return formatted_conversations
            
        except Exception as e:
            print(f"Error retrieving user conversations: {e}")
            return []
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete an entire conversation"""
        try:
            return self.chat_repository.delete_conversation(conversation_id)
        except Exception as e:
            print(f"Error deleting conversation: {e}")
            return False
    
    # Private helper methods
    
    def _generate_conversation_id(self) -> str:
        """Generate a unique conversation ID"""
        return f"conv_{uuid.uuid4().hex[:12]}"
    
    def _get_rag_context(self, query: str) -> Dict[str, Any]:
        """Retrieve relevant context using RAG system"""
        try:
            # This will be implemented with LangChain RAG
            # For now, return a placeholder
            return {
                "context": "Medical context from RAG system",
                "sources": [],
                "relevance_score": 0.8
            }
        except Exception as e:
            print(f"Error retrieving RAG context: {e}")
            return {"context": "", "sources": [], "relevance_score": 0.0}
    
    def _generate_llm_response(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response using LLM with medical context"""
        try:
            import os
            import requests
            
            # Get configuration from environment
            ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
            ollama_model = os.getenv('OLLAMA_MODEL', 'AlthosKal/medicoia')
            
            # Create medical prompt
            medical_prompt = f"""Eres un asistente médico especializado. Tu trabajo es proporcionar información médica educativa y sugerencias generales.

IMPORTANTE: Siempre recuerda al usuario que:
1. Esta información es solo educativa
2. No reemplaza la consulta médica profesional
3. Debe buscar atención médica si tiene síntomas graves

Contexto médico relevante: {context.get("context", "No hay contexto específico disponible")}

Pregunta del usuario: {message}

Respuesta médica profesional:"""
            
            # Make direct request to Ollama API
            try:
                response = requests.post(
                    f"{ollama_url}/api/generate",
                    json={
                        "model": ollama_model,
                        "prompt": medical_prompt,
                        "stream": False
                    },
                    timeout=30  # Reduced timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    llm_response = result.get("response", "")
                    if not llm_response:
                        raise Exception("Empty response from Ollama")
                else:
                    raise Exception(f"Ollama API error: {response.status_code}")
                    
            except requests.exceptions.Timeout:
                raise Exception("Ollama model took too long to respond")
            except requests.exceptions.ConnectionError:
                raise Exception("Cannot connect to Ollama. Make sure it's running.")
            
            return {
                "content": llm_response.strip(),
                "confidence": 0.85,
                "reasoning": "Análisis basado en conocimiento médico especializado"
            }
            
        except Exception as e:
            print(f"Error generating LLM response: {e}")
            return {
                "content": f"Como asistente médico especializado, puedo ayudarte con información sobre '{message}'. Sin embargo, es importante recordar que esta información es solo educativa y no reemplaza la consulta con un profesional médico. Te recomiendo consultar con un doctor para una evaluación completa de tu situación.",
                "confidence": 0.7,
                "reasoning": "Respuesta de respaldo por error en el sistema principal"
            }
    
    def _process_medical_image(self, image_data: bytes) -> Optional[Dict[str, Any]]:
        """Process and validate medical image"""
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Basic validation
            if image.format not in ['JPEG', 'PNG', 'TIFF', 'DICOM']:
                return None
            
            # Resize if too large (for LLM processing)
            max_size = (1024, 1024)
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Convert to base64 for LLM processing
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            image_b64 = base64.b64encode(buffer.getvalue()).decode()
            
            return {
                "image_data": image_b64,
                "format": image.format,
                "size": image.size,
                "mode": image.mode
            }
            
        except Exception as e:
            print(f"Error processing medical image: {e}")
            return None
    
    def _analyze_image_with_llm(self, processed_image: Dict[str, Any], text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze image using multimodal LLM (LLaVA)"""
        try:
            # This will be implemented with LangChain + LLaVA
            # For now, return a placeholder analysis
            return {
                "findings": ["Placeholder finding 1", "Placeholder finding 2"],
                "confidence": 0.82,
                "recommendations": ["Recommendation 1", "Recommendation 2"],
                "image_quality": "Good",
                "technical_details": {
                    "image_size": processed_image["size"],
                    "format": processed_image["format"]
                }
            }
        except Exception as e:
            print(f"Error analyzing image with LLM: {e}")
            return {
                "findings": [],
                "confidence": 0.0,
                "recommendations": [],
                "error": str(e)
            }
    
    def _combine_text_image_analysis(self, text: str, image_analysis: Dict[str, Any], text_context: Dict[str, Any]) -> Dict[str, Any]:
        """Combine text and image analysis into comprehensive response"""
        try:
            # This will integrate both analyses using LangChain
            combined_content = f"""
            Based on the image analysis and your description: {text}
            
            Image Analysis Results:
            {image_analysis.get('findings', [])}
            
            Recommendations:
            {image_analysis.get('recommendations', [])}
            
            Please note: This is an AI-assisted analysis and should be reviewed by a medical professional.
            """
            
            return {
                "content": combined_content.strip(),
                "confidence": min(image_analysis.get("confidence", 0.8), text_context.get("relevance_score", 0.8)),
                "reasoning": "Combined analysis of image and textual symptoms"
            }
            
        except Exception as e:
            print(f"Error combining analyses: {e}")
            return {
                "content": "Error combining analysis results",
                "confidence": 0.0,
                "reasoning": "Error in processing"
            }