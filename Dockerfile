FROM python:3.10-slim

# Install system dependencies (ffmpeg is crucial for yt-dlp)
RUN apt-get update && apt-get install -y ffmpeg curl && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy all files
COPY . .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Render dynamically assigns a PORT. We use 10000 as fallback.
ENV PORT=10000
EXPOSE $PORT

# Run the Engine using Gunicorn (Production Grade WSGI)
# Timeout set to 600s (10 mins) to prevent crashes on large downloads
CMD gunicorn app:app --bind 0.0.0.0:$PORT --timeout 600 --workers 2
