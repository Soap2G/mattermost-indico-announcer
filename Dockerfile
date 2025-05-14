FROM python:3.11-slim

WORKDIR /app

COPY bot.py .

RUN pip install Flask requests APScheduler

EXPOSE 8080

CMD ["python", "bot.py"]