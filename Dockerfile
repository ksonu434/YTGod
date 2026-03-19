# 1. Base OS (Linux + Python)
FROM python:3.10-slim

# 2. Install FFmpeg & Node.js (The Magic Tools)
RUN apt-get update && \
    apt-get install -y ffmpeg nodejs npm && \
    apt-get clean

# 3. Setup Working Directory
WORKDIR /app
COPY . /app

# 4. Install Python Libraries
RUN pip install --no-cache-dir -r requirements.txt

# 5. Ignite the God Mode Engine
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:app"]