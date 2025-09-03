# use official python image 
FROM python:3.10-slim

# Set env variables
ENV PYTHONWRITEBYTECODE=1 
ENV PYTHONUNBUFFERED=1 

# SET working directory
WORKDIR /app

# Install dependencies 
RUN apt-get update && apt-get install -y \
    build-essential poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt and install Python dependencies
COPY requirements.txt .

# Copy project files 
COPY . .

# Install Dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 
EXPOSE 8080 

# Replace last CMD in prod 
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "4"]
