import os
import tempfile
import logging
import json
from typing import List, Dict, Any
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
from utils.document_processor import process_documents
from utils.rag_chatbot import RAGChatbot
from utils.vector_store import VectorStore
from utils.web_scraper import website_to_documents, get_website_text_content

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, 
            static_folder="static",
            template_folder="templates")

# Enable debug mode
app.debug = True
app.logger.setLevel(logging.DEBUG)
logger.info("Flask app initialized in debug mode")

# Initialize vector store
vector_store = VectorStore()

# Initialize RAG chatbot
rag_chatbot = RAGChatbot(vector_store)

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
        
        logger.debug(f"Received chat message: {message}")
        
        if not message:
            return jsonify({"error": "Message is required"}), 400
        
        response, sources = rag_chatbot.generate_response(message)
        logger.debug(f"Generated response: {response}")
        
        return jsonify({
            "response": response,
            "sources": sources
        })
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({"error": f"Error processing chat: {str(e)}"}), 500

@app.route("/upload", methods=["POST"])
def upload_files():
    """Upload and process documents"""
    try:
        if "files" not in request.files:
            logger.warning("No files found in request")
            return jsonify({"error": "No files provided"}), 400
        
        files = request.files.getlist("files")
        logger.debug(f"Received {len(files)} files for upload")
        
        if not files or all(file.filename == "" for file in files):
            logger.warning("Empty file list or all files have empty names")
            return jsonify({"error": "No valid files provided"}), 400
        
        processed_files = []
        failed_files = []
        
        for file in files:
            if file.filename == "":
                continue
                
            filename = secure_filename(file.filename)
            logger.debug(f"Processing file: {filename}")
            
            # Create a temporary file
            temp_file_path = None
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
                    # Write content to temporary file
                    file.save(temp_file)
                    temp_file_path = temp_file.name
                
                logger.debug(f"Temporary file created at: {temp_file_path}")
                
                # Process the document
                documents = process_documents(temp_file_path, filename)
                
                # Check if we got valid documents
                if documents and len(documents) > 0:
                    # Add documents to vector store
                    vector_store.add_documents(documents)
                    processed_files.append(filename)
                    logger.info(f"Successfully processed file: {filename} ({len(documents)} chunks)")
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
        return jsonify({"error": f"Error uploading documents: {str(e)}"}), 500

@app.route("/health")
def health_check():
    """Health check endpoint"""
    logger.info("Health check endpoint called")
    return jsonify({"status": "ok", "message": "RAG Chatbot is operational"})

@app.route("/test")
def test_page():
    """Test endpoint to verify the server is working"""
    logger.info("Test endpoint called")
    return "RAG Chatbot test page - Server is running!"

@app.route("/process-website", methods=["POST"])
def process_website():
    """Process a website URL and add its content to the knowledge base"""
    try:
        data = request.json
        url = data.get("url")
        max_pages = data.get("max_pages", 5)  # Default to 5 pages
        max_depth = data.get("max_depth", 1)  # Default to depth 1 (just the page)
        
        logger.debug(f"Received website processing request for URL: {url}")
        
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
        
        logger.info(f"Successfully processed website {url} with {len(documents)} document chunks from {len(unique_urls)} pages")
        
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
