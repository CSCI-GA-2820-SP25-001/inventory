FROM python:3.9-slim

WORKDIR /app

# Copy requirements
COPY Pipfile Pipfile.lock ./

# Install dependencies
RUN pip install pipenv && \
    pipenv install --deploy --system && \
    pip install gunicorn

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

# Expose port
EXPOSE 8080

# Run the application
CMD gunicorn --bind 0.0.0.0:$PORT wsgi:app
