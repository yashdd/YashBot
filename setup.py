#!/usr/bin/env python3
"""
Simple setup script for YashBot RAG Chatbot
"""

from setuptools import setup, find_packages

setup(
    name="yashbot-rag-chatbot",
    version="1.0.0",
    description="A RAG chatbot powered by Google Gemini and Pinecone",
    author="Yash Deshpande",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "flask",
        "langchain",
        "langchain-google-genai",
        "langchain-community",
        "langchain-text-splitters",
        "gunicorn",
        "pypdf",
        "pdfminer-six",
        "python-docx",
        "unstructured",
        "trafilatura",
        "python-multipart",
        "werkzeug",
        "openpyxl",
        "email-validator",
        "python-dotenv",
        "pinecone"
    ],
    entry_points={
        'console_scripts': [
            'yashbot=main:main',
        ],
    },
)
