import os
import logging
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
# from langchain_openai import OpenAIEmbeddings  # Commented out OpenAI embeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings  # Added Gemini embeddings
from langchain_community.vectorstores import Pinecone
from pinecone import Pinecone as PineconeClient

logger = logging.getLogger(__name__)

class VectorStore:
    """
    Manages the vector storage for document embeddings
    """
    
    def __init__(self):
        """
        Initialize the vector store with Google Gemini embeddings and Pinecone
        """
        try:
            # Get API keys from environment variables
            google_api_key = os.environ.get("GOOGLE_API_KEY")
            pinecone_api_key = os.environ.get("PINECONE_API_KEY")
            
            if not google_api_key:
                logger.warning("GOOGLE_API_KEY not set in environment variables")
            
            if not pinecone_api_key:
                raise ValueError("PINECONE_API_KEY is required for vector storage")
            
            # Initialize embeddings
            self.embeddings = GoogleGenerativeAIEmbeddings(
                google_api_key=google_api_key,
                model="models/embedding-001"  # Google's text embedding model
            )
            
            # Initialize Pinecone client
            self.pinecone_client = PineconeClient(api_key=pinecone_api_key)
            logger.info("Pinecone client initialized")
            
            # Initialize vector store
            self.vector_store = None
            self._initialize_pinecone()
            

        except Exception as e:
            logger.error(f"Error initializing vector store: {str(e)}")
            raise
    
    def _initialize_pinecone(self):
        """Initialize Pinecone index"""
        try:
            index_name = "rag-chatbot-index"
            
            # Check if index exists
            if index_name in self.pinecone_client.list_indexes().names():
                # Load existing index
                self.vector_store = Pinecone.from_existing_index(
                    index_name, 
                    self.embeddings
                )
                logger.info("Loaded existing Pinecone index")
            else:
                # Create new index with spec
                from pinecone import ServerlessSpec
                self.pinecone_client.create_index(
                    name=index_name,
                    dimension=768,  # Google embedding dimension
                    metric="cosine",
                                    spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
                )
                self.vector_store = None
                logger.info("Created new Pinecone index")
        except Exception as e:
            logger.error(f"Error initializing Pinecone: {e}")
            raise
    
    def add_documents(self, documents: List[Document]) -> None:
        """
        Add documents to the vector store
        """
        try:
            if not documents:
                logger.warning("No documents to add")
                return
            

            
            if self.vector_store is None:
                # Create new Pinecone vector store
                index_name = "rag-chatbot-index"
                logger.info(f"Creating new Pinecone vector store with index: {index_name}")
                self.vector_store = Pinecone.from_documents(
                    documents, 
                    self.embeddings,
                    index_name=index_name
                )
                logger.info(f"✅ Successfully created Pinecone vector store with {len(documents)} documents")
            else:
                # Add to existing Pinecone vector store
                logger.info(f"Adding {len(documents)} documents to existing Pinecone index")
                self.vector_store.add_documents(documents)
                logger.info(f"✅ Successfully added {len(documents)} documents to Pinecone")
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {str(e)}")
            raise
    
    def search(self, query: str, k: int = 4) -> List[Document]:
        """
        Search for similar documents in the vector store
        
        Args:
            query: The query string
            k: Number of documents to return
            
        Returns:
            List of similar documents
        """
        try:
            if self.vector_store is None:
                logger.warning("No documents in vector store")
                return []
            

            similar_docs = self.vector_store.similarity_search(query, k=k)

            
            return similar_docs
        except Exception as e:
            logger.error(f"Error searching vector store: {str(e)}")
            raise

    def get_storage_info(self) -> Dict[str, Any]:
        """
        Get information about the current storage status
        """
        try:
            info = {
                "storage_type": "Pinecone (persistent)",
                "has_vector_store": self.vector_store is not None,
                "document_count": 0
            }
            
            if self.vector_store:
                try:
                    # Get Pinecone index statistics
                    index_stats = self.vector_store.index.describe_index_stats()
                    info["document_count"] = index_stats.get("total_vector_count", 0)
                    info["index_name"] = "rag-chatbot-index"
                    info["dimension"] = index_stats.get("dimension", 768)
                except Exception as e:
                    logger.error(f"Error getting Pinecone stats: {e}")
                    info["error"] = str(e)
            
            return info
        except Exception as e:
            logger.error(f"Error getting storage info: {e}")
            return {"error": str(e)}
