import os
import logging
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

# LangChain imports for RAG
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import MongoDBAtlasVectorSearch
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_ollama import OllamaLLM

from repository.fragment_document_repository import FragmentDocumentRepository
from repository.metadata_document_repository import MetadataDocumentRepository


class RAGService(ABC):
    """Abstract RAG service interface"""
    
    @abstractmethod
    def add_documents(self, documents: List[str], metadata: List[Dict[str, Any]]) -> bool:
        """Add documents to the knowledge base"""
        pass
    
    @abstractmethod
    def query(self, question: str, top_k: int = 5) -> Dict[str, Any]:
        """Query the knowledge base"""
        pass
    
    @abstractmethod
    def get_relevant_context(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Get relevant context for a query"""
        pass


class LangChainRAGService(RAGService):
    """
    LangChain-based RAG service implementation for medical knowledge retrieval.
    Uses OpenAI embeddings and MongoDB Atlas for vector storage.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.fragment_repo = FragmentDocumentRepository()
        self.metadata_repo = MetadataDocumentRepository()
        
        # Initialize embeddings
        self.embeddings = self._initialize_embeddings()
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""]
        )
        
        # Initialize LLM for generation
        self.llm = self._initialize_llm()
        
        # Initialize vector store
        self.vector_store = self._initialize_vector_store()
        
        # Initialize QA chain
        self.qa_chain = self._initialize_qa_chain()
    
    def _initialize_embeddings(self) -> OpenAIEmbeddings:
        """Initialize OpenAI embeddings"""
        try:
            api_key = os.getenv('OPENAI_KEY') or os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_KEY or OPENAI_API_KEY not found in environment variables")
            
            return OpenAIEmbeddings(
                openai_api_key=api_key,
                model=os.getenv('EMBEDDING_MODEL', 'text-embedding-ada-002')
            )
        except Exception as e:
            self.logger.error(f"Error initializing embeddings: {e}")
            raise
    
    def _initialize_llm(self) -> OllamaLLM:
        """Initialize Ollama LLM"""
        try:
            return OllamaLLM(
                base_url=os.getenv('OLLAMA_URL', 'http://localhost:11434'),
                model=os.getenv('LLAVA_MODEL', 'llava:latest'),
                temperature=0.1,
                top_p=0.9
            )
        except Exception as e:
            self.logger.error(f"Error initializing LLM: {e}")
            raise
    
    def _initialize_vector_store(self) -> Optional[MongoDBAtlasVectorSearch]:
        """Initialize MongoDB Atlas vector store"""
        try:
            mongodb_uri = os.getenv('DATABASE_URL') or os.getenv('MONGODB_URI')
            if not mongodb_uri:
                self.logger.warning("DATABASE_URL not configured, vector search will use fallback")
                return None
            
            # This would work with MongoDB Atlas
            # For local development, we'll use the fragment repository directly
            return None
            
        except Exception as e:
            self.logger.error(f"Error initializing vector store: {e}")
            return None
    
    def _initialize_qa_chain(self) -> Optional[RetrievalQA]:
        """Initialize QA chain with retrieval"""
        try:
            if not self.vector_store:
                return None
            
            # Medical-specific prompt template
            template = """
            Eres un asistente médico especializado. Utiliza el siguiente contexto para responder a la pregunta médica.
            Si no tienes suficiente información, indica claramente las limitaciones.
            
            IMPORTANTE: Esta es una asistencia diagnóstica y NO reemplaza el juicio médico profesional.
            
            Contexto médico:
            {context}
            
            Pregunta: {question}
            
            Respuesta detallada:
            """
            
            prompt = PromptTemplate(
                template=template,
                input_variables=["context", "question"]
            )
            
            return RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.vector_store.as_retriever(search_kwargs={"k": 5}),
                chain_type_kwargs={"prompt": prompt},
                return_source_documents=True
            )
            
        except Exception as e:
            self.logger.error(f"Error initializing QA chain: {e}")
            return None
    
    def add_documents(self, documents: List[str], metadata: List[Dict[str, Any]]) -> bool:
        """Add medical documents to the knowledge base"""
        try:
            if len(documents) != len(metadata):
                raise ValueError("Documents and metadata lists must have the same length")
            
            for doc_text, doc_metadata in zip(documents, metadata):
                # Save metadata document
                metadata_id = self.metadata_repo.save({
                    "document_title": doc_metadata.get("title", "Untitled Medical Document"),
                    "document_type": doc_metadata.get("type", "medical"),
                    "metadata": doc_metadata,
                    "valid": True,
                    "version": 1
                })
                
                # Split document into chunks
                chunks = self.text_splitter.split_text(doc_text)
                
                # Process each chunk
                for i, chunk in enumerate(chunks):
                    # Generate embedding
                    embedding = self.embeddings.embed_query(chunk)
                    
                    # Save fragment
                    self.fragment_repo.save({
                        "id_metadata_document": metadata_id,
                        "chunk_index": i,
                        "content": chunk,
                        "embedding": embedding
                    })
            
            self.logger.info(f"Successfully added {len(documents)} documents to knowledge base")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding documents: {e}")
            return False
    
    def query(self, question: str, top_k: int = 5) -> Dict[str, Any]:
        """Query the medical knowledge base"""
        try:
            if self.qa_chain:
                # Use LangChain QA chain
                result = self.qa_chain({"query": question})
                
                return {
                    "answer": result["result"],
                    "source_documents": [
                        {
                            "content": doc.page_content,
                            "metadata": doc.metadata,
                            "score": getattr(doc, 'score', 0.0)
                        }
                        for doc in result.get("source_documents", [])
                    ],
                    "confidence": 0.8  # This would be calculated based on retrieval scores
                }
            else:
                # Fallback to manual retrieval and generation
                context_docs = self.get_relevant_context(question, top_k)
                
                # Create context string
                context = "\n\n".join([doc["content"] for doc in context_docs])
                
                # Generate response using LLM
                prompt = f"""
                Basándote en el siguiente contexto médico, responde a la pregunta:
                
                Contexto: {context}
                
                Pregunta: {question}
                
                Respuesta:
                """
                
                response = self.llm(prompt)
                
                return {
                    "answer": response,
                    "source_documents": context_docs,
                    "confidence": 0.7
                }
                
        except Exception as e:
            self.logger.error(f"Error querying knowledge base: {e}")
            return {
                "answer": "Lo siento, no pude procesar tu consulta en este momento.",
                "source_documents": [],
                "confidence": 0.0,
                "error": str(e)
            }
    
    def get_relevant_context(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Get relevant context using vector similarity search"""
        try:
            # Generate query embedding
            query_embedding = self.embeddings.embed_query(query)
            
            # Search for similar fragments
            results = self.fragment_repo.vector_search(query_embedding, limit=top_k)
            
            # Format results
            context_docs = []
            for result in results:
                context_docs.append({
                    "content": result.get("content", ""),
                    "metadata": {
                        "fragment_id": str(result.get("_id")),
                        "metadata_doc_id": result.get("id_metadata_document"),
                        "chunk_index": result.get("chunk_index", 0)
                    },
                    "score": result.get("score", 0.0)
                })
            
            return context_docs
            
        except Exception as e:
            self.logger.error(f"Error getting relevant context: {e}")
            return []
    
    def add_medical_knowledge_base(self) -> bool:
        """Add sample medical knowledge for testing"""
        try:
            sample_docs = [
                """
                La migraña es un tipo de dolor de cabeza caracterizado por episodios recurrentes de cefalea 
                pulsátil, generalmente unilateral, acompañada de náuseas, vómitos y sensibilidad a la luz y al sonido.
                
                Síntomas principales:
                - Dolor de cabeza intenso y pulsátil
                - Náuseas y vómitos
                - Fotofobia (sensibilidad a la luz)
                - Fonofobia (sensibilidad al sonido)
                - Duración: 4-72 horas si no se trata
                
                Tratamiento:
                - Analgésicos simples (paracetamol, ibuprofeno)
                - Triptanes para casos severos
                - Reposo en ambiente oscuro y silencioso
                - Hidratación adecuada
                """,
                
                """
                La neumonía es una infección respiratoria que inflama los sacos aéreos de uno o ambos pulmones.
                Puede ser causada por bacterias, virus u hongos.
                
                Síntomas principales:
                - Tos con flema (puede ser verdosa, amarilla o con sangre)
                - Fiebre, escalofríos y sudoración
                - Dificultad para respirar
                - Dolor en el pecho al toser o respirar
                - Fatiga y debilidad
                
                Diagnóstico:
                - Radiografía de tórax
                - Análisis de sangre
                - Cultivo de esputo
                
                Tratamiento:
                - Antibióticos para neumonía bacteriana
                - Antivirales para neumonía viral
                - Reposo y hidratación
                - Medicamentos para la fiebre y el dolor
                """,
                
                """
                La diabetes mellitus tipo 2 es una condición crónica que afecta la forma en que el cuerpo 
                procesa el azúcar en sangre (glucosa).
                
                Síntomas:
                - Sed excesiva
                - Micción frecuente
                - Hambre extrema
                - Pérdida de peso inexplicable
                - Fatiga
                - Visión borrosa
                - Heridas que sanan lentamente
                
                Manejo:
                - Dieta balanceada y baja en carbohidratos
                - Ejercicio regular
                - Medicamentos antidiabéticos
                - Monitoreo regular de glucosa
                - Control de peso
                
                Complicaciones:
                - Enfermedad cardiovascular
                - Neuropatía diabética
                - Retinopatía diabética
                - Nefropatía diabética
                """
            ]
            
            metadata = [
                {
                    "title": "Guía Clínica: Migraña",
                    "type": "neurología",
                    "specialty": "neurología",
                    "source": "Manual de Neurología SENA",
                    "keywords": ["migraña", "cefalea", "dolor de cabeza", "fotofobia", "náuseas"]
                },
                {
                    "title": "Protocolo: Neumonía Adquirida en Comunidad",
                    "type": "neumología",
                    "specialty": "medicina interna",
                    "source": "Guías de Práctica Clínica",
                    "keywords": ["neumonía", "tos", "fiebre", "dificultad respiratoria", "radiografía"]
                },
                {
                    "title": "Manual: Diabetes Mellitus Tipo 2",
                    "type": "endocrinología",
                    "specialty": "endocrinología",
                    "source": "Protocolo de Diabetes SENA",
                    "keywords": ["diabetes", "glucosa", "sed", "micción", "fatiga"]
                }
            ]
            
            return self.add_documents(sample_docs, metadata)
            
        except Exception as e:
            self.logger.error(f"Error adding medical knowledge base: {e}")
            return False