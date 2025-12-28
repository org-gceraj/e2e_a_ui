# Base image
FROM python:3.10-slim

# Working directory
WORKDIR /app

# Copy dependency list first (layer caching)
COPY docker/requirements.ui.txt docker/requirements.ui.txt

# Install dependencies
RUN pip install --no-cache-dir -r docker/requirements.ui.txt

# Copy source code
COPY scripts/ scripts/

# Expose Streamlit port
EXPOSE 8501
EXPOSE 30007

# Start Streamlit app
CMD ["streamlit", "run", "scripts/app.py", "--server.port", "8501",  "--server.address", "0.0.0.0"]
