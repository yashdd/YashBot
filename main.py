import os
from dotenv import load_dotenv
load_dotenv()
print("DEBUG: API KEY from env:", os.getenv("GOOGLE_API_KEY"))  # Changed from OPENAI_API_KEY for debug

from app import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
