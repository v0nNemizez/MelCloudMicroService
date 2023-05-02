FROM python:3.10-slim

USER root
RUN useradd melcloud

RUN apt-get update

RUN mkdir app
COPY melcloud.py /app
COPY app.py /app
COPY req.txt /app
COPY config.json /app

WORKDIR /app
RUN pip3 install -r req.txt
RUN chmod 777 /app

USER melcloud
WORKDIR /app
EXPOSE 8000

CMD ["gunicorn"  , "--bind", "0.0.0.0:8000", "app:app"]