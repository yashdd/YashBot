import os
print("DEBUG: API KEY from env:", os.getenv("OPENAI_API_KEY"))

import logging
from typing import List, Dict, Any, Optional
import faiss
import numpy as np
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

logger = logging.getLogger(__name__)

class VectorStore:
    """
    Manages the vector storage for document embeddings
    """
    
    def __init__(self):
        """
        Initialize the vector store with OpenAI embeddings
        """
        try:
            # Get API key from environment variable
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                logger.warning("OPENAI_API_KEY not set in environment variables")
            
            self.embeddings = OpenAIEmbeddings(openai_api_key=api_key)
            self.vector_store = None
            logger.debug("Vector store initialized")
        except Exception as e:
            logger.error(f"Error initializing vector store: {str(e)}")
            raise
    
    def add_documents(self, documents: List[Document]) -> None:
        """
        Add documents to the vector store
        """
        try:
            if not documents:
                logger.warning("No documents to add")
                return
            
            logger.debug(f"Adding {len(documents)} documents to vector store")
            
            if self.vector_store is None:
                # Create new vector store
                self.vector_store = FAISS.from_documents(documents, self.embeddings)
                logger.debug("Created new vector store")
            else:
                # Add to existing vector store
                self.vector_store.add_documents(documents)
                logger.debug("Added to existing vector store")
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
            
            logger.debug(f"Searching for: {query}")
            similar_docs = self.vector_store.similarity_search(query, k=k)
            logger.debug(f"Found {len(similar_docs)} similar documents")
            
            return similar_docs
        except Exception as e:
            logger.error(f"Error searching vector store: {str(e)}")
            raise
