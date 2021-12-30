# syntax=docker/dockerfile:1
FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /ws
RUN pip3 install websocket-server
RUN pip3 install websockets
COPY . /ws/