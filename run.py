#!/usr/bin/env python
import logging
from app import app

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logging.info("Starting Flask application directly in debug mode")
    
    # Run the app
    app.run(host="0.0.0.0", port=5000, debug=True)