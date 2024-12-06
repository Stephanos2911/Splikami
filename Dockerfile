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

WORKDIR /app

# Set default PORT to 8000 if not already set
ENV PORT=8000

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create database directory and set permissions
RUN mkdir -p /app/database && chmod 777 /app/database

# Set volume for persistent database storage
VOLUME ["/app/database"]

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port 8000
EXPOSE 8000

# Run migrations and start the server
CMD ["sh", "-c", "python manage.py makemigrations SplikamiApp && python manage.py migrate && gunicorn SplikamiProject.wsgi:application --bind 0.0.0.0:8000"]