FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY service /app/service
COPY shared /app/shared
COPY src /app/src
COPY schemas /app/schemas
COPY simulation /app/simulation
COPY tests /app/tests

RUN useradd --create-home --uid 10001 spectra
USER 10001

CMD ["python", "/app/service/main.py"]
