# docker build --tag exchangerate:1.0 .
FROM python:3.8-slim-bullseye

LABEL org.opencontainers.image.authors="jair.solis@pm.me"

WORKDIR /usr/src/app

RUN apt-get -y update

# Install Python requirements
ADD ./requirements.txt .
RUN pip3 install -r requirements.txt

# Copy project
COPY ./src/*.py ./

CMD [ "python3", "uvicorn", "main:app"]