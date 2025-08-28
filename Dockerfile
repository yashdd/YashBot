FROM python:3.11.11-slim

# FUCK POETRY - PURE PIP ONLY
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=10000

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies with pip (NO POETRY ANYWHERE)
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Expose port
EXPOSE $PORT

# Run the application
CMD gunicorn app:app --bind 0.0.0.0:$PORT --timeout 60 --workers 1
