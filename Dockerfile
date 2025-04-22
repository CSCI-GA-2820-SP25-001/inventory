FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
COPY service ./service
COPY wsgi.py .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "wsgi.py"]