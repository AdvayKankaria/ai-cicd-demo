FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY services/payment/ /app/services/payment/
CMD ["uvicorn", "services.payment.main:app", "--host", "0.0.0.0", "--port", "8000"]
