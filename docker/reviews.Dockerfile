FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY services/reviews/ /app/services/reviews/
CMD ["uvicorn", "services.reviews.main:app", "--host", "0.0.0.0", "--port", "8000"]
