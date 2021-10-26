FROM ubuntu:20.04
RUN apt update && apt install -y python3 python3-pip libpq-dev
COPY requirements.txt /
RUN pip3 install -r /requirements.txt && rm /requirements.txt && mkdir /app
ENV PYTHONUNBUFFERED=1
RUN apt install -y postgresql-client
