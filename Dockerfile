FROM python:3.11-slim

# ffmpeg is required by openai-whisper to actually decode audio.
# Render's native Python runtime has no apt access, so we need this Dockerfile.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt requirements-whisper.txt ./
# openai-whisper's old build script needs pkg_resources, which recent
# setuptools versions (81+) removed entirely.
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir "setuptools<81" wheel

# Install everything except whisper normally.
RUN pip install --no-cache-dir -r requirements.txt

# Install whisper with build isolation OFF — otherwise pip creates a fresh
# throwaway environment for the build step that ignores the pinned setuptools
# above and pulls its own (too new) copy from PyPI every time.
RUN pip install --no-cache-dir --no-build-isolation -r requirements-whisper.txt

COPY . .

# Render sets $PORT at runtime and expects the app to bind to 0.0.0.0
CMD uvicorn main:app --host 0.0.0.0 --port $PORT