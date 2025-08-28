#!/usr/bin/env python3
"""
Test script to verify all dependencies are working and not deprecated
"""

import sys
import warnings

def test_imports():
    """Test that all required packages can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import flask
        print(f"✅ Flask {flask.__version__}")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False
        
    try:
        import langchain
        print(f"✅ LangChain {langchain.__version__}")
    except ImportError as e:
        print(f"❌ LangChain import failed: {e}")
        return False
        
    try:
        import langchain_google_genai
        print(f"✅ LangChain Google GenAI imported")
    except ImportError as e:
        print(f"❌ LangChain Google GenAI import failed: {e}")
        return False
        
    try:
        import pinecone
        print(f"✅ Pinecone {pinecone.__version__}")
    except ImportError as e:
        print(f"❌ Pinecone import failed: {e}")
        return False
        
    try:
        from langchain_core.output_parsers import StrOutputParser
        print(f"✅ LangChain Core StrOutputParser")
    except ImportError as e:
        print(f"❌ StrOutputParser import failed: {e}")
        return False
        
    try:
        from langchain.prompts import PromptTemplate
        print(f"✅ LangChain PromptTemplate")
    except ImportError as e:
        print(f"❌ PromptTemplate import failed: {e}")
        return False
        
    return True

def test_deprecated_warnings():
    """Check for deprecation warnings"""
    print("\n⚠️  Testing for deprecation warnings...")
    
    # Capture warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        
        try:
            # Test LangChain imports that might be deprecated
            from langchain_google_genai import ChatGoogleGenerativeAI
            from langchain.prompts import PromptTemplate
            from langchain_core.output_parsers import StrOutputParser
            
            # Test Pinecone
            from pinecone import Pinecone, ServerlessSpec
            
            if w:
                print(f"⚠️  Found {len(w)} warnings:")
                for warning in w:
                    print(f"   - {warning.category.__name__}: {warning.message}")
            else:
                print("✅ No deprecation warnings found")
                
        except Exception as e:
            print(f"❌ Error during warning test: {e}")
            return False
            
    return True

def test_app_structure():
    """Test that the app structure is correct"""
    print("\n📁 Testing app structure...")
    
    import os
    required_files = [
        "app.py",
        "main.py", 
        "requirements.txt",
        "runtime.txt",
        "Procfile",
        "render.yaml",
        "utils/rag_chatbot.py",
        "utils/vector_store.py",
        "utils/document_processor.py",
        "utils/web_scraper.py",
        "templates/index.html",
        "static/css/styles.css",
        "static/js/script.js"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
            
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files present")
        return True

def test_environment():
    """Test environment setup"""
    print("\n🌍 Testing environment...")
    
    import os
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major == 3 and python_version.minor >= 11:
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"⚠️  Python version {python_version.major}.{python_version.minor} (requires 3.11+)")
        
    # Check for .env template
    env_vars = ["GOOGLE_API_KEY", "PINECONE_API_KEY"]
    for var in env_vars:
        if os.getenv(var):
            print(f"✅ {var} is set")
        else:
            print(f"⚠️  {var} not set (add to .env file)")
            
    return True

def main():
    """Run all tests"""
    print("🚀 YashBot Setup Test\n")
    
    tests = [
        test_imports,
        test_deprecated_warnings, 
        test_app_structure,
        test_environment
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()
            
    print(f"📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! Your setup is ready.")
        return True
    else:
        print("❌ Some tests failed. Check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
