FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY services/returns/ /app/services/returns/
CMD ["uvicorn", "services.returns.main:app", "--host", "0.0.0.0", "--port", "8000"]
