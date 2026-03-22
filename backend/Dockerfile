FROM python:3.12-slim

# Prevent Python from writing .pyc files and buffering stdout oddly in containers
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Where the app lives inside the container
WORKDIR /app

# Install OS deps sometimes needed for psycopg2 (uncomment if pip build fails)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential libpq-dev \
#     && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (better Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app ./app

# The port uvicorn will listen on inside the container
EXPOSE 8000

# Start FastAPI (module path must match your package: app.main -> app.main:app)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]