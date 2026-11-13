FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY .streamlit/ ./.streamlit/
COPY assets/ ./assets/
COPY src/ ./src/
COPY app.py ./

EXPOSE 8080

HEALTHCHECK CMD curl --fail http://localhost:8080/_stcore/health || exit 1

CMD ["sh", "-c", "streamlit run app.py --server.port=${PORT:-8080} --server.address=0.0.0.0 --server.headless=true --server.enableCORS=false --server.enableXsrfProtection=false"]
