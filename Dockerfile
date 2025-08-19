FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements-server.txt .
RUN pip install --no-cache-dir -r requirements-server.txt

# Copy the application code
COPY . .

# Set environment variables
ENV TRANSPORT=sse
ENV PORT=9004
ENV PYTHONPATH=/app

# Expose the port
EXPOSE $PORT

# Run the aha-mcp server
CMD ["python", "main.py"]
