FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    PORT=8080 \
    SPECTRA_DEPLOYMENT_MODE=CLOUD_RUN

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY scripts /app/scripts
COPY src /app/src
COPY schemas /app/schemas
COPY simulation /app/simulation
COPY tests /app/tests
COPY demo /app/demo
COPY output /app/output
COPY docs /app/docs

RUN useradd --create-home --uid 10001 spectra
USER 10001

CMD ["python", "/app/scripts/run_evidence_console.py"]
