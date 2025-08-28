# Deployment Guide

## Quick Deploy to Render

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Switch to pip - remove Poetry"
   git push
   ```

2. **Deploy on Render**
   - Go to [render.com](https://render.com)
   - Connect your GitHub repo
   - Render will auto-detect Python and use `render.yaml`

3. **Set Environment Variables** (in Render dashboard):
   - `GOOGLE_API_KEY`: Your Google Gemini API key
   - `PINECONE_API_KEY`: Your Pinecone API key

4. **Deploy** - Render will automatically:
   - Run `pip install -r requirements.txt`
   - Start with `gunicorn app:app --bind 0.0.0.0:$PORT --timeout 60 --workers 1`

## Local Development

```bash
# Clone and setup
git clone <your-repo>
cd PersonalRAGAssistant

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GOOGLE_API_KEY=your_key_here
export PINECONE_API_KEY=your_key_here

# Run the app
python main.py
```

## Files Structure (Clean & Simple)

```
PersonalRAGAssistant/
├── app.py                 # Main Flask application
├── main.py               # Entry point for local development
├── requirements.txt      # Python dependencies (pip)
├── runtime.txt          # Python version for Render
├── Procfile             # Process definition for deployment
├── render.yaml          # Render deployment configuration
├── setup.py             # Optional: package setup
├── .gitignore           # Git ignore file
├── README.md            # Main documentation
├── DEPLOYMENT.md        # This file
├── utils/               # Utility modules
│   ├── document_processor.py
│   ├── rag_chatbot.py
│   ├── vector_store.py
│   └── web_scraper.py
├── templates/           # HTML templates
│   └── index.html
└── static/              # CSS, JS, images
    ├── css/
    └── js/
```

## Why We Switched from Poetry to pip

- **Simpler deployment**: pip is universally supported
- **No configuration hassles**: No `pyproject.toml` issues
- **Render compatibility**: Works out of the box
- **Cleaner structure**: Less files, less complexity
- **Standard Python**: Most developers know pip

## Environment Variables

| Variable | Description | Required |
|----------|-------------|-----------|
| `GOOGLE_API_KEY` | Google Gemini API key | Yes |
| `PINECONE_API_KEY` | Pinecone vector database key | Yes |

## 🔧 **Poetry Detection Prevention**

If Render still tries to use Poetry, the project includes these files to force pip:
- ✅ `render.yaml` - Explicit pip build commands
- ✅ `.buildpacks` - Forces Python buildpack
- ✅ `.python-version` - Python version specification
- ✅ `runtime.txt` - Backup Python version

That's it! Much simpler than Poetry. 🎉
