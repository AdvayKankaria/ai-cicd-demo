FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY services/shipping/ /app/services/shipping/
CMD ["uvicorn", "services.shipping.main:app", "--host", "0.0.0.0", "--port", "8000"]
