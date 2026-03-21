FROM python:3.11

WORKDIR /app

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
