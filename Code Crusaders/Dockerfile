# Use official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install git (required for fetching from github if needed)
# and clean up apt cache to reduce image size
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port that Streamlit uses
EXPOSE 8501

# Streamlit specific configuration
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# Create a volume for the SQLite database so history persists
VOLUME ["/app/data"]
ENV CRUSADER_DB_PATH=/app/data/review_history.db

# Run the application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
