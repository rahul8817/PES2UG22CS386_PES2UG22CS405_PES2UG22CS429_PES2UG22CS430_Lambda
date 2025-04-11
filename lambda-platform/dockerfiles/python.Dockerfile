FROM python:3.9-slim

WORKDIR /app

COPY function.python /app/function.py

CMD ["python", "function.py"]

