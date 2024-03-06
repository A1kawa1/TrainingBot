FROM python:3.10-slim

RUN mkdir /app

COPY requirements.txt /app

COPY TrainingBot/ /app

WORKDIR /app

RUN pip3 install -r requirements.txt --no-cache-dir