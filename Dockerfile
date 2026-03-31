# 1. Base OS (Linux + Python)
FROM python:3.10-slim

# 2. Install FFmpeg & Node.js (The Magic Tools)
RUNFROM python:3.10-slim

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
CMD gunicorn app:app --bind 0.0.0.0:$PORT --timeout 600 --workers 2 apt-get update && \
    apt-get install -y ffmpeg nodejs npm && \
    apt-get clean

# 3. Setup Working Directory
WORKDIR /app
COPY . /app

# 4. Install Python Libraries
RUN pip install --no-cache-dir -r requirements.txt

# 5. Ignite the God Mode Engine
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:app"]
