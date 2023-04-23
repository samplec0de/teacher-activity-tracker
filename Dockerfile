# Image based on python 3.11
FROM python:3.11

# Install requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy contents from app directory to /app
COPY app /app

# Set working directory
WORKDIR /

# Run bot.py
CMD ["python", "/app/bot.py"]
