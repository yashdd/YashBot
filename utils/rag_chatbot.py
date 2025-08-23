import os
import logging
from typing import List, Tuple, Dict, Any
# from langchain_openai import ChatOpenAI  # Commented out OpenAI import
from langchain_google_genai import ChatGoogleGenerativeAI  # Added Gemini import
from langchain.chains import ConversationChain, LLMChain
from langchain.chains.question_answering import load_qa_chain
from langchain.memory import ConversationBufferMemory
from utils.vector_store import VectorStore

logger = logging.getLogger(__name__)

class RAGChatbot:
    """
    RAG (Retrieval-Augmented Generation) chatbot using LangChain and Google Gemini
    """
    
    def __init__(self, vector_store: VectorStore):
       
        try:
            # Get API key from environment variable
            api_key = os.environ.get("GOOGLE_API_KEY")  # Changed from OPENAI_API_KEY
            if not api_key:
                logger.warning("GOOGLE_API_KEY not set in environment variables")
            
            # Initialize the language model
            # Using Google's Gemini Pro model
            self.llm = ChatGoogleGenerativeAI(
                google_api_key=api_key,  # Changed from openai_api_key
                model="gemini-1.5-pro",  # Updated to correct model name
                temperature=0.7,
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

                return
                
            # Check if there are documents in the vector store
            # For Pinecone, we need to check the index stats instead of index_to_docstore_id
            try:
                # Access the Pinecone index directly - try different access patterns
                if hasattr(self.vector_store.vector_store, 'index'):
                    index_stats = self.vector_store.vector_store.index.describe_index_stats()
                elif hasattr(self.vector_store.vector_store, '_index'):
                    index_stats = self.vector_store.vector_store._index.describe_index_stats()
                else:
                    # If we can't access the index directly, assume it exists and proceed
    
                    index_stats = {"total_vector_count": 1}  # Assume documents exist
                
                total_vectors = index_stats.get("total_vector_count", 0)
                
                if total_vectors == 0:
                    logger.warning("Vector store has no documents")
                    self.chain = None
                    return
                

            except Exception as e:
                logger.error(f"Error checking vector store stats: {e}")
                # If stats check fails, assume documents exist and proceed

            
            # Create a retriever
            self.retriever = self.vector_store.vector_store.as_retriever(
                search_kwargs={"k": 4}
            )

            
            # Create a QA chain
            try:
                self.qa_chain = load_qa_chain(
                    llm=self.llm,
                    chain_type="stuff" 
                )

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

            except Exception as conv_error:
                logger.error(f"Failed to create conversation chain: {str(conv_error)}")
                raise
            
            # Create a simple wrapper function to maintain compatibility with the existing code
            self.chain = self._chain_wrapper
            

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

            
            # Get relevant documents from the retriever
            docs = self.retriever.get_relevant_documents(query)

            
            if not docs:
                answer = "I couldn't find any relevant information in the documents you provided. Please try asking a different question or upload more documents."
            else:
                # Run the question answering chain
                answer = self.qa_chain.run(input_documents=docs, question=query)

            
            # Update conversation memory
            try:
                self.conversation_chain.predict(input=query)

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
            

            
            return response, sources
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"I encountered an error: {str(e)}", []
