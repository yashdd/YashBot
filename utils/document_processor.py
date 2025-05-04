import os
import logging
from typing import List
from langchain_community.document_loaders import (
    PyPDFLoader, 
    TextLoader, 
    CSVLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredPowerPointLoader,
    UnstructuredExcelLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

# Configure text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
)

def get_loader_for_file(file_path: str):
    """
    Get the appropriate document loader based on file extension
    """
    ext = os.path.splitext(file_path)[1].lower()
    logger.debug(f"Getting loader for file with extension: {ext}")
    
    try:
        if ext == '.pdf':
            return PyPDFLoader(file_path)
        elif ext == '.txt':
            return TextLoader(file_path)
        elif ext == '.csv':
            return CSVLoader(file_path)
        elif ext in ['.doc', '.docx']:
            return UnstructuredWordDocumentLoader(file_path)
        elif ext in ['.ppt', '.pptx']:
            return UnstructuredPowerPointLoader(file_path)
        elif ext in ['.xls', '.xlsx']:
            return UnstructuredExcelLoader(file_path)
        else:
            # For unsupported types, try using the text loader with a warning
            logger.warning(f"Unsupported file type: {ext}, attempting to use TextLoader")
            return TextLoader(file_path)
    except Exception as e:
        logger.error(f"Error creating loader for {file_path}: {str(e)}")
        raise ValueError(f"Could not create document loader for {file_path}: {str(e)}")

def process_documents(file_path: str, file_name: str) -> List[Document]:
    """
    Process documents with the appropriate loader and split into chunks
    """
    try:
        logger.debug(f"Processing document: {file_name}")
        
        # Load document
        loader = get_loader_for_file(file_path)
        documents = loader.load()
        
        # Add metadata with the source filename
        for doc in documents:
            doc.metadata['source'] = file_name
        
        # Split document into chunks
        split_docs = text_splitter.split_documents(documents)
        
        logger.debug(f"Document {file_name} processed into {len(split_docs)} chunks")
        return split_docs
        
    except Exception as e:
        logger.error(f"Error processing document {file_name}: {str(e)}")
        raise Exception(f"Error processing document {file_name}: {str(e)}")
