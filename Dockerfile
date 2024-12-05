FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    tesseract-ocr-nld \
    tesseract-ocr-spa \
    tesseract-ocr-por \
    tesseract-ocr-fra \
    tesseract-ocr-eng \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Create directory for SQLite database
RUN mkdir -p /app/data

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Set volume for persistent database storage
VOLUME ["/app/data"]

# Run migrations and start the server
CMD python manage.py migrate && gunicorn SplikamiProject.wsgi:application --bind 0.0.0.0:$PORT