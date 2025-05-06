FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

# Set the working directory
WORKDIR /app

# Copy requirements files
COPY Pipfile Pipfile.lock ./

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip pipenv && \
    pipenv install --system --deploy && \
    pip install gunicorn

# Copy the application code
COPY . .

# Expose the port
EXPOSE $PORT

# Run the application
CMD gunicorn --bind=0.0.0.0:$PORT --access-logfile=- wsgi:app
