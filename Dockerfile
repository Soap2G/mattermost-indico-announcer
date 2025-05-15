FROM python:3.11-slim

WORKDIR /app

COPY bot.py .
COPY requirements.txt .

RUN pip install -r requirements.txt

EXPOSE 8080

CMD ["python", "bot.py"]