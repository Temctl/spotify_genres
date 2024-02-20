FROM ubuntu:latest

RUN apt-get update && apt-get install -y vim -y curl -y cron -y python3-pip -y curl
RUN pip install --upgrade pip

COPY .app /app
WORKDIR /app
COPY requirements.txt .requirements.txt

ENV FLASK_APP=app

RUN pip install -r .requirements.txt
CMD "python app.py"