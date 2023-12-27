FROM python:3.8-slim-buster

WORKDIR /app

COPY client-server-code ./code
COPY data ./data

RUN pip install pyarrow pandas

WORKDIR /app/code
CMD ["python", "server.py"]
