import os
import logging
from typing import List, Tuple, Dict, Any
# from langchain_openai import ChatOpenAI  # Commented out OpenAI import
from langchain_google_genai import ChatGoogleGenerativeAI  # Added Gemini import
from langchain.chains import ConversationChain, LLMChain
from langchain.chains.question_answering import load_qa_chain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
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
            
            # Initialize chain attributes to None (lazy initialization)
            self.chain = None
            self.retriever = None
            self.qa_chain = None
            self.conversation_chain = None
            
            # Don't initialize RAG chain on startup to save memory
            # self.initialize_rag_chain()
            

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

            
            # Create a custom prompt template for YashBot
            custom_prompt_template = """You are YashBot, an AI assistant trained on information about Yash. You are helpful, friendly, and knowledgeable about Yash's background, interests, and experiences.

IMPORTANT GUIDELINES:
1. If anyone asks about Yash's suitability for a job, role, or position, be extremely positive and highlight Yash's strengths, skills, and achievements. Always present Yash as an excellent candidate.
2. NEVER share any private, personal, or sensitive information about Yash (exact addresses, exact birth dates, financial information, etc.). It's OK to share: name, phone number, email address, and general location (city/state/country) as these are professional contact details.
3. If asked about private details, politely redirect to professional information only.
4. Always present Yash in the best possible light while being honest about his actual skills and experiences.
5. For recruiters or hiring managers, emphasize Yash's technical skills, problem-solving abilities, and professional achievements.
6. IMPORTANT: Write responses in plain text without any markdown formatting, bullet points, or special characters. Use simple paragraphs and clear sentences.

Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.

Context: {context}

Question: {question}

Answer:"""

            # Create a QA chain with custom prompt
            try:
                prompt = PromptTemplate(
                    template=custom_prompt_template,
                    input_variables=["context", "question"]
                )
                
                self.qa_chain = load_qa_chain(
                    llm=self.llm,
                    chain_type="stuff",
                    prompt=prompt
                )

            except Exception as qa_error:
                logger.error(f"Failed to create QA chain: {str(qa_error)}")
                raise
            
            # Set up conversation chain with proper memory configuration
            try:
                # Custom prompt for conversation chain
                conversation_prompt = PromptTemplate(
                    input_variables=["history", "input"],
                    template="""You are YashBot, an AI assistant trained on information about Yash. You are helpful, friendly, and knowledgeable about Yash's background, interests, and experiences.

IMPORTANT GUIDELINES:
1. If anyone asks about Yash's suitability for a job, role, or position, be extremely positive and highlight Yash's strengths, skills, and achievements. Always present Yash as an excellent candidate.
2. NEVER share any private, personal, or sensitive information about Yash (exact addresses, exact birth dates, financial information, etc.). It's OK to share: name, phone number, email address, and general location (city/state/country) as these are professional contact details.
3. If asked about private details, politely redirect to professional information only.
4. Always present Yash in the best possible light while being honest about his actual skills and experiences.
5. For recruiters or hiring managers, emphasize Yash's technical skills, problem-solving abilities, and professional achievements.
6. IMPORTANT: Write responses in plain text without any markdown formatting, bullet points, or special characters. Use simple paragraphs and clear sentences.

Current conversation:
{history}
Human: {input}
YashBot:"""
                )
                
                self.conversation_chain = ConversationChain(
                    llm=self.llm,
                    memory=self.memory,
                    prompt=conversation_prompt,
                    verbose=True
                )

            except Exception as conv_error:
                logger.error(f"Failed to create conversation chain: {str(conv_error)}")
                raise
            
            # Create a simple wrapper function to maintain compatibility with the existing code
            self.chain = self._chain_wrapper
            logger.info("✅ RAG chain initialized successfully")
            

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
            
            # Check if this is a recruiter/job-related question
            recruiter_keywords = [
                "good fit", "suitable", "candidate", "hire", "recruit", "position", 
                "role", "job", "employment", "work", "team", "company", "organization",
                "skills", "experience", "qualifications", "background", "resume", "cv"
            ]
            
            # Check if this is asking for private/personal information
            private_keywords = [
                "exact address", "street address", "home address", "birth", "date", "age", "salary",
                "income", "money", "bank", "account", "ssn", "social security", "id",
                "passport", "driver license", "personal", "private", "home", "family"
            ]
            
            is_recruiter_question = any(keyword in query.lower() for keyword in recruiter_keywords)
            is_private_question = any(keyword in query.lower() for keyword in private_keywords)
            
            # Get relevant documents from the retriever
            docs = self.retriever.invoke(query)

            
            if not docs:
                if is_private_question:
                    answer = "I'm sorry, but I cannot share any private or sensitive information about Yash. I can share his name, phone number, email, and general location as these are professional contact details. For any other private information, please contact Yash directly."
                elif is_recruiter_question:
                    answer = "Based on what I know about Yash, he would be an excellent fit for any role! He's a highly skilled and motivated individual with strong technical abilities and a great work ethic. I'd be happy to discuss his specific qualifications and experience if you have any particular questions about his background or skills."
                else:
                    answer = "I couldn't find any relevant information about Yash in my knowledge base for that question. Please try asking something else about Yash, or ask me about topics I might know about from the documents I've been trained on."
            else:
                # Run the question answering chain
                answer = self.qa_chain.run(input_documents=docs, question=query)
                
                # If it's asking for private information, add privacy warning
                if is_private_question:
                    answer += "\n\nNote: I can share Yash's name, phone number, email, and general location as professional contact details. For any other private information, please contact Yash directly."
                
                # If it's a recruiter question, add extra positive reinforcement
                elif is_recruiter_question:
                    answer += "\n\nFrom what I can tell, Yash would be an outstanding addition to any team. He demonstrates strong problem-solving skills, technical expertise, and a collaborative approach to work."

            
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
            # Limit query length to prevent memory issues
            if len(query) > 1000:
                query = query[:1000]
                logger.warning("Query truncated to prevent memory issues")
            
            # If no documents are loaded yet
            if self.vector_store.vector_store is None:
                response = "I don't have any knowledge about Yash loaded yet. Please check with the administrator to ensure my knowledge base is properly set up."
                return response, []
            
            # Check if vector store has documents
            try:
                if hasattr(self.vector_store.vector_store, 'index'):
                    index_stats = self.vector_store.vector_store.index.describe_index_stats()
                elif hasattr(self.vector_store.vector_store, '_index'):
                    index_stats = self.vector_store.vector_store._index.describe_index_stats()
                else:
                    index_stats = {"total_vector_count": 0}
                
                total_vectors = index_stats.get("total_vector_count", 0)
                if total_vectors == 0:
                    response = "I don't have any documents about Yash in my knowledge base yet. Please check with the administrator to ensure my knowledge base is properly set up."
                    return response, []
            except Exception as e:
                logger.warning(f"Could not check vector store stats: {e}")
                # Continue anyway, let the initialization handle it
            
            # If chain is not initialized, initialize it
            if self.chain is None:
                logger.info("Initializing RAG chain...")
                self.initialize_rag_chain()
                
                # If still None, return error
                if self.chain is None:
                    logger.error("Failed to initialize RAG chain")
                    response = "I'm having trouble accessing my knowledge base about Yash. Please check with the administrator to ensure everything is properly configured."
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
            
            # Force garbage collection after RAG operations
            import gc
            gc.collect()
            
            return response, sources
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"I encountered an error: {str(e)}", []
