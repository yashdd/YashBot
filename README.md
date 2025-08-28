# RAG Chatbot

A Retrieval-Augmented Generation (RAG) chatbot built with Python, Flask, and LangChain.

## Features

- **Document Processing**: Upload and process PDF, DOCX, and TXT files
- **Website Scraping**: Extract content from websites to use as knowledge sources
- **Vector Database**: Store and retrieve document embeddings using Pinecone
- **Conversational Interface**: Chat interface with context-aware responses
- **Source Tracking**: Show the source of information in responses

## Tech Stack

- **Backend**: Python, Flask, Gunicorn
- **NLP**: LangChain, Google Gemini API, Pinecone
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
   export GOOGLE_API_KEY=your_google_api_key
   export PINECONE_API_KEY=your_pinecone_api_key
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

## Deployment

### Render Deployment

1. **Fork/Clone** this repository to your GitHub account
2. **Connect to Render**:
   - Go to [render.com](https://render.com)
   - Create a new **Web Service**
   - Connect your GitHub repository
3. **Configure Environment Variables**:
   - `GOOGLE_API_KEY`: Your Google Gemini API key
   - `PINECONE_API_KEY`: Your Pinecone API key
4. **Build Settings** (Render will auto-detect):
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
5. **Deploy** and wait for build to complete

### Alternative: Use render.yaml (Auto-deploy)

If you have the `render.yaml` file in your repo, Render will automatically configure everything!

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

## License

MIT
