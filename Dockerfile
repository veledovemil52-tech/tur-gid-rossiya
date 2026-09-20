FROM python:3.11-slim

WORKDIR /app

COPY bot/requirements.txt ./bot/requirements.txt
RUN pip install --no-cache-dir -r ./bot/requirements.txt

COPY bot/bot.py ./bot/bot.py

ENV PYTHONUNBUFFERED=1

CMD ["python", "bot/bot.py"]
