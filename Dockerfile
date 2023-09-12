# Use the official Python runtime as a parent image
FROM python:3.9-bullseye

RUN apt-get update && apt-get install -y build-essential \
        && apt-get install libportaudio2 libasound2  libportaudiocpp0 portaudio19-dev libasound-dev libsndfile1-dev -y
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg

# Set the working directory
WORKDIR /app

# Copy the Poetry configuration and lock files
COPY ./pyproject.toml /app/pyproject.toml
COPY ./poetry.lock /app/poetry.lock

RUN pip install --no-cache-dir --upgrade poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev --no-interaction --no-ansi
RUN pip install gunicorn
RUN pip install pyaudio
RUN pip install — upgrade pip && pip install -r requirements.txt

# Copy your application files
COPY main.py /app/main.py
COPY config.yaml /app/config.yaml
COPY callcenter /app/callcenter

# Specify the command to run your application
CMD exec gunicorn -b :$PORT main:app