FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc && \
    apt-get clean

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Make entrypoint.sh executable
RUN chmod +x entrypoint.sh

# Run migrations and start server via entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
