from dotenv import load_dotenv
load_dotenv()

from app import app

def main():
    """Main entry point for the application"""
    app.run(host="0.0.0.0", port=5000, debug=True)

if __name__ == "__main__":
    main()
