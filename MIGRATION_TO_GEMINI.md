# Migration from OpenAI to Google Gemini API

This document outlines the changes made to migrate the RAG chatbot from OpenAI API to Google Gemini API.

## Changes Made

### 1. Dependencies Updated (`pyproject.toml`)
- **Removed**: `openai` and `langchain-openai` packages
- **Added**: `langchain-google-genai` and `google-generativeai` packages

### 2. Language Model (`utils/rag_chatbot.py`)
- **Before**: `ChatOpenAI` with `gpt-3.5-turbo` model
- **After**: `ChatGoogleGenerativeAI` with `gemini-pro` model
- **API Key**: Changed from `OPENAI_API_KEY` to `GOOGLE_API_KEY`

### 3. Embeddings (`utils/vector_store.py`)
- **Before**: `OpenAIEmbeddings`
- **After**: `GoogleGenerativeAIEmbeddings` with `models/embedding-001` model
- **API Key**: Changed from `OPENAI_API_KEY` to `GOOGLE_API_KEY`

### 4. Environment Variables
- **Before**: `OPENAI_API_KEY`
- **After**: `GOOGLE_API_KEY`

### 5. Documentation (`README.md`)
- Updated tech stack description
- Updated setup instructions
- Updated environment variable examples

## Setup Instructions

1. **Get Google API Key**:
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Copy the API key

2. **Set Environment Variable**:
   ```bash
   export GOOGLE_API_KEY=your_google_api_key_here
   ```
   
   Or create a `.env` file:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   ```

3. **Install Dependencies**:
   ```bash
   poetry install
   ```
   or
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**:
   ```bash
   python run.py
   ```

## Key Differences

### API Models
- **OpenAI**: Used `gpt-3.5-turbo` for chat and `text-embedding-ada-002` for embeddings
- **Gemini**: Uses `gemini-pro` for chat and `models/embedding-001` for embeddings

### API Key Management
- Both APIs use similar API key authentication
- Google API keys are obtained from Google AI Studio
- OpenAI API keys are obtained from OpenAI platform

### Performance
- Gemini Pro is comparable to GPT-3.5-turbo in performance
- Google's embedding model provides similar quality to OpenAI's embeddings

## Troubleshooting

1. **API Key Issues**: Ensure your `GOOGLE_API_KEY` is set correctly
2. **Model Access**: Make sure you have access to Gemini Pro and embedding models
3. **Rate Limits**: Google API has different rate limits than OpenAI
4. **Content Policy**: Gemini has different content policies than OpenAI

## Benefits of Migration

1. **Cost**: Potentially lower costs with Google's pricing
2. **Integration**: Better integration with Google's ecosystem
3. **Performance**: Comparable performance to OpenAI models
4. **Features**: Access to Google's latest AI capabilities
