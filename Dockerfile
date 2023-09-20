FROM python:3.6.6

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH "${PYTHONPATH}:/code"

WORKDIR /code

COPY requirements.txt requirements.txt
RUN \
    pip install --no-cache-dir --upgrade pip && \
    pip install -r /code/requirements.txt
