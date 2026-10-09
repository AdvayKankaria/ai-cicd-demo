FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY services/checkout/ /app/services/checkout/
CMD ["uvicorn", "services.checkout.main:app", "--host", "0.0.0.0", "--port", "8000"]
