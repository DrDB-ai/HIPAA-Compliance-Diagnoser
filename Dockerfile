# Use official Python image as base image
FROM python:3.9-slim

# Install system-level dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq-dev \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV STREAMLIT_SERVER_PORT=8501

# Set working directory in the container
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Streamlit application files into the container
COPY . .

# Expose the Streamlit server port
EXPOSE 8501

# Command to run the Streamlit application
CMD ["streamlit", "run", "--server.port", "8501", "app.py", "--server.fileWatcherType", "none"]

