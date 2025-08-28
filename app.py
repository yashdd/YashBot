import os
import tempfile
import logging
import json
import gc
from typing import List, Dict, Any
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from utils.document_processor import process_documents
from utils.rag_chatbot import RAGChatbot
from utils.vector_store import VectorStore
from utils.web_scraper import website_to_documents, get_website_text_content

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, 
            static_folder="static",
            template_folder="templates")

# Optimize for memory usage
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def check_memory_usage():
    """Check current memory usage and log it"""
    try:
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        logger.info(f"Current memory usage: {memory_mb:.2f} MB")
        return memory_mb
    except ImportError:
        return 0
    except Exception as e:
        logger.warning(f"Could not check memory usage: {e}")
        return 0

def force_garbage_collection():
    """Force garbage collection to free memory"""
    try:
        gc.collect()
    except Exception as e:
        logger.warning(f"Error during garbage collection: {e}")

logger.info("Flask app initialized")

# Initialize vector store with error handling
try:
    vector_store = VectorStore()
    logger.info("Successfully initialized VectorStore")
except Exception as e:
    logger.error(f"Failed to initialize VectorStore: {str(e)}")
    vector_store = None

# Initialize RAG chatbot with error handling
try:
    if vector_store:
        rag_chatbot = RAGChatbot(vector_store)
        logger.info("Successfully initialized RAGChatbot")
    else:
        rag_chatbot = None
        logger.warning("RAGChatbot not initialized due to VectorStore failure")
except Exception as e:
    logger.error(f"Failed to initialize RAGChatbot: {str(e)}")
    rag_chatbot = None


@app.route("/")
def index():
    """Render the main page"""
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    """Process a chat message and return a response"""
    try:
        data = request.json
        message = data.get("message")
        
        if not message:
            return jsonify({"error": "Message is required"}), 400
        
        if rag_chatbot is None:
            return jsonify({
                "response": "I'm having trouble accessing my knowledge base. Please check the logs for more information.",
                "sources": []
            }), 500
        
        response, sources = rag_chatbot.generate_response(message)
        
        # Clean up memory after processing
        force_garbage_collection()
        
        return jsonify({
            "response": response,
            "sources": sources
        })
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        # Clean up memory even on error
        force_garbage_collection()
        return jsonify({"error": f"Error processing chat: {str(e)}"}), 500

@app.route("/upload", methods=["POST"])
def upload_files():
    """Upload and process documents"""
    try:
        if "files" not in request.files:
            logger.warning("No files found in request")
            return jsonify({"error": "No files provided"}), 400
        
        files = request.files.getlist("files")
        
        if not files or all(file.filename == "" for file in files):
            logger.warning("Empty file list or all files have empty names")
            return jsonify({"error": "No valid files provided"}), 400
        
        processed_files = []
        failed_files = []
        
        for file in files:
            if file.filename == "":
                continue
                
            filename = secure_filename(file.filename)
            
            # Create a temporary file
            temp_file_path = None
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
                    # Write content to temporary file
                    file.save(temp_file)
                    temp_file_path = temp_file.name
                

                
                # Process the document
                documents = process_documents(temp_file_path, filename)

                
                # Check if we got valid documents
                if documents and len(documents) > 0:
                    # Add documents to vector store

                    vector_store.add_documents(documents)
                    processed_files.append(filename)

                else:
                    logger.warning(f"No document chunks extracted from: {filename}")
                    failed_files.append({"name": filename, "reason": "No text content extracted"})
                
                # Remove temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    temp_file_path = None
            except Exception as e:
                logger.error(f"Error processing file {filename}: {str(e)}")
                failed_files.append({"name": filename, "reason": str(e)})
                
                # Clean up temporary file if it exists
                if temp_file_path and os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
        
        # Check if any files were processed successfully
        if processed_files:
            # Re-initialize the RAG chain now that we have documents
            rag_chatbot.initialize_rag_chain()
            
            response = {
                "message": f"Successfully processed {len(processed_files)} documents", 
                "files": processed_files
            }
            
            if failed_files:
                response["failed_files"] = failed_files
                response["warning"] = f"{len(failed_files)} files could not be processed"
            
            # Clean up memory after successful upload
            force_garbage_collection()
            
            return jsonify(response)
        else:
            # If all files failed, return an error
            logger.error(f"All file uploads failed: {failed_files}")
            return jsonify({
                "error": "All file uploads failed", 
                "failed_files": failed_files
            }), 500
    except Exception as e:
        logger.error(f"Error in upload endpoint: {str(e)}")
        # Clean up memory even on error
        force_garbage_collection()
        return jsonify({"error": f"Error uploading documents: {str(e)}"}), 500

@app.route("/test-pinecone")
def test_pinecone():
    """Test Pinecone connection and index status"""
    try:
        from pinecone import Pinecone
        
        # Get environment variables
        pinecone_api_key = os.environ.get("PINECONE_API_KEY")
        
        result = {
            "pinecone_api_key_set": bool(pinecone_api_key),
            "pinecone_initialized": False,
            "index_exists": False,
            "index_stats": None,
            "error": None
        }
        
        if not pinecone_api_key:
            result["error"] = "Missing Pinecone API key"
            return jsonify(result)
        
        try:
            # Initialize Pinecone with new API
            pc = Pinecone(api_key=pinecone_api_key)
            result["pinecone_initialized"] = True
            
            # Check if index exists
            index_name = "rag-chatbot-index"
            if index_name in pc.list_indexes().names():
                result["index_exists"] = True
                
                # Get index stats
                index = pc.Index(index_name)
                stats = index.describe_index_stats()
                result["index_stats"] = stats
            else:
                result["error"] = f"Index '{index_name}' not found"
                
        except Exception as e:
            result["error"] = f"Pinecone error: {str(e)}"
            
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error testing Pinecone: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/storage-status")
def storage_status():
    """Check the current storage status"""
    try:
        storage_info = vector_store.get_storage_info()
        return jsonify(storage_info)
    except Exception as e:
        logger.error(f"Error getting storage status: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/health")
def health_check():
    """Health check endpoint"""
    try:
        from datetime import datetime
        status = {
            "status": "ok",
            "message": "RAG Chatbot is operational",
            "timestamp": datetime.now().isoformat(),
            "environment": {
                "google_api_key_set": bool(os.environ.get("GOOGLE_API_KEY")),
                "pinecone_api_key_set": bool(os.environ.get("PINECONE_API_KEY"))
            }
        }
        return jsonify(status)
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route("/test")
def test_page():
    """Test endpoint to verify the server is working"""
    return "RAG Chatbot test page - Server is running!"

@app.route("/process-website", methods=["POST"])
def process_website():
    """Process a website URL and add its content to the knowledge base"""
    try:
        data = request.json
        url = data.get("url")
        max_pages = data.get("max_pages", 5)  # Default to 5 pages
        max_depth = data.get("max_depth", 1)  # Default to depth 1 (just the page)
        
        if not url:
            return jsonify({"error": "URL is required"}), 400
        
        # Convert website to documents
        documents = website_to_documents(url, max_pages=max_pages, max_depth=max_depth)
        
        if not documents:
            logger.warning(f"No content extracted from website: {url}")
            return jsonify({
                "error": "Could not extract content from the provided URL",
                "url": url
            }), 400
        
        # Add documents to vector store
        vector_store.add_documents(documents)
        
        # Re-initialize the RAG chain
        rag_chatbot.initialize_rag_chain()
        
        page_urls = [doc.metadata.get("source") for doc in documents]
        unique_urls = list(set(page_urls))
        
        return jsonify({
            "message": f"Successfully processed website content", 
            "url": url,
            "pages_processed": len(unique_urls),
            "chunks_created": len(documents),
            "processed_urls": unique_urls[:10]  # Return first 10 URLs (limit response size)
        })
    except Exception as e:
        logger.error(f"Error processing website: {str(e)}")
        return jsonify({"error": f"Error processing website: {str(e)}"}), 500
