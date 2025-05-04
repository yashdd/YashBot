import os
import logging
from typing import List, Tuple, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain, LLMChain
from langchain.chains.question_answering import load_qa_chain
from langchain.memory import ConversationBufferMemory
from utils.vector_store import VectorStore

logger = logging.getLogger(__name__)

class RAGChatbot:
    """
    RAG (Retrieval-Augmented Generation) chatbot using LangChain and OpenAI
    """
    
    def __init__(self, vector_store: VectorStore):
        """
        Initialize the RAG chatbot
        
        Args:
            vector_store: The vector store for document retrieval
        """
        try:
            # Get API key from environment variable
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                logger.warning("OPENAI_API_KEY not set in environment variables")
            
            # Initialize the language model
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            self.llm = ChatOpenAI(
                openai_api_key=api_key,
                model="gpt-4o", 
                temperature=0.7
            )
            
            # Initialize conversation memory
            self.memory = ConversationBufferMemory(
                memory_key="history", 
                return_messages=False
            )
            
            # Store the vector store
            self.vector_store = vector_store
            
            # Initialize the RAG chain
            self.initialize_rag_chain()
            
            logger.debug("RAG chatbot initialized")
        except Exception as e:
            logger.error(f"Error initializing RAG chatbot: {str(e)}")
            raise
    
    def initialize_rag_chain(self) -> None:
        """
        Initialize the Retrieval-Augmented Generation chain
        """
        try:
            if not self.vector_store.vector_store:
                self.chain = None
                logger.debug("RAG chain not initialized (no documents yet)")
                return
                
            # Check if there are documents in the vector store
            if self.vector_store.vector_store.index_to_docstore_id is None or not self.vector_store.vector_store.index_to_docstore_id:
                logger.warning("Vector store has no documents")
                self.chain = None
                return
            
            logger.debug(f"Initializing RAG chain with {len(self.vector_store.vector_store.index_to_docstore_id)} documents")
            
            # Create a retriever
            self.retriever = self.vector_store.vector_store.as_retriever(
                search_kwargs={"k": 4}
            )
            logger.debug("Retriever created successfully")
            
            # Create a QA chain
            try:
                self.qa_chain = load_qa_chain(
                    llm=self.llm,
                    chain_type="stuff" 
                )
                logger.debug("QA chain created successfully")
            except Exception as qa_error:
                logger.error(f"Failed to create QA chain: {str(qa_error)}")
                raise
            
            # Set up conversation chain with proper memory configuration
            try:
                self.conversation_chain = ConversationChain(
                    llm=self.llm,
                    memory=self.memory,
                    verbose=True
                )
                logger.debug("Conversation chain created successfully")
            except Exception as conv_error:
                logger.error(f"Failed to create conversation chain: {str(conv_error)}")
                raise
            
            # Create a simple wrapper function to maintain compatibility with the existing code
            self.chain = self._chain_wrapper
            
            logger.debug("RAG chain components initialized with retriever")
        except Exception as e:
            logger.error(f"Error initializing RAG chain: {str(e)}")
            self.chain = None
    
    def _chain_wrapper(self, inputs: Dict[str, str]) -> Dict[str, Any]:
        """
        Wrapper function to maintain compatibility with the ConversationalRetrievalChain interface
        
        Args:
            inputs: Dictionary with a "question" key containing the user query
            
        Returns:
            Dictionary with "answer" and "source_documents" keys
        """
        try:
            query = inputs.get("question", "")
            logger.debug(f"Processing query in chain wrapper: {query}")
            
            # Get relevant documents from the retriever
            docs = self.retriever.get_relevant_documents(query)
            logger.debug(f"Retrieved {len(docs)} relevant documents")
            
            if not docs:
                answer = "I couldn't find any relevant information in the documents you provided. Please try asking a different question or upload more documents."
            else:
                # Run the question answering chain
                answer = self.qa_chain.run(input_documents=docs, question=query)
                logger.debug(f"Generated answer with QA chain")
            
            # Update conversation memory
            try:
                self.conversation_chain.predict(input=query)
                logger.debug("Updated conversation memory")
            except Exception as memory_error:
                logger.warning(f"Error updating conversation memory: {str(memory_error)}")
            
            return {
                "answer": answer,
                "source_documents": docs
            }
        except Exception as e:
            logger.error(f"Error in chain wrapper: {str(e)}")
            return {
                "answer": f"Error processing your question: {str(e)}",
                "source_documents": []
            }
    
    def generate_response(self, query: str) -> Tuple[str, List[str]]:
        """
        Generate a response for the user query
        
        Args:
            query: The user's query
            
        Returns:
            Tuple of (response, sources)
        """
        try:
            logger.debug(f"Generating response for: {query}")
            
            # If no documents are loaded yet
            if self.vector_store.vector_store is None:
                response = "I don't have any knowledge yet. Please upload some documents first."
                return response, []
            
            # If chain is not initialized, initialize it
            if self.chain is None:
                self.initialize_rag_chain()
                
                # If still None, return error
                if self.chain is None:
                    response = "I'm having trouble accessing my knowledge base. Please try uploading documents again."
                    return response, []
            
            # Get response using the chain
            result = self.chain({"question": query})
            
            # Extract the response
            response = result.get("answer", "I couldn't generate a response.")
            
            # Get unique sources
            source_docs = result.get("source_documents", [])
            sources = []
            for doc in source_docs:
                source = doc.metadata.get("source")
                if source and source not in sources:
                    sources.append(source)
            
            logger.debug(f"Generated response with {len(sources)} sources")
            
            return response, sources
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"I encountered an error: {str(e)}", []
