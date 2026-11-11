FROM ubuntu:24.04

RUN apt-get update && apt-get install -y python3

WORKDIR /app
COPY app.py .

CMD ["python3", "app.py"]