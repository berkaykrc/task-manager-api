FROM python:3.8-slim-buster

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /usr/src/app

# Install dependencies
COPY pyproject.toml ./
RUN pip install --upgrade pip
RUN pip install poetry
RUN poetry install

COPY taskmanager .

