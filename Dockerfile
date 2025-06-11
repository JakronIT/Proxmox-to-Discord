FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install flask pyyaml requests

# Copy application
COPY app.py .
COPY config.yaml .

# Run as non-root
RUN useradd -r appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

CMD ["python", "app.py"]
