# RAG Chatbot

A Retrieval-Augmented Generation (RAG) chatbot built with Python, Flask, and LangChain.

## Features

- **Document Processing**: Upload and process PDF, DOCX, and TXT files
- **Website Scraping**: Extract content from websites to use as knowledge sources
- **Vector Database**: Store and retrieve document embeddings using FAISS
- **Conversational Interface**: Chat interface with context-aware responses
- **Source Tracking**: Show the source of information in responses

## Tech Stack

- **Backend**: Python, Flask, Gunicorn
- **NLP**: LangChain, OpenAI API, FAISS
- **Web Scraping**: Trafilatura
- **Document Processing**: PyPDF, Python-DOCX
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5

## Setup Instructions

1. Clone the repository
   ```
   git clone https://github.com/yourusername/rag-chatbot.git
   cd rag-chatbot
   ```

2. Install dependencies
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables
   ```
   export OPENAI_API_KEY=your_openai_api_key
   ```

4. Run the application
   ```
   python run.py
   ```

5. Access the application at `http://localhost:5000`

## Usage

1. **Upload Documents**: Click the "Upload" button to add PDF, DOCX, or TXT files to the knowledge base
2. **Add Websites**: Enter a website URL to extract content and add it to the knowledge base
3. **Chat**: Ask questions about the content of your documents or websites
4. **View Sources**: See which documents or websites provided the information in the response

## Project Structure

- `app.py`: Flask application with routes and handlers
- `utils/`: Utility modules
  - `document_processor.py`: Handles document loading and processing
  - `vector_store.py`: Manages the vector database
  - `rag_chatbot.py`: Implements the RAG functionality
  - `web_scraper.py`: Handles website content extraction
- `templates/`: HTML templates
- `static/`: CSS, JavaScript, and other static files

## License

MIT