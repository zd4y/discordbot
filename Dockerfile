FROM python:3.8.3-alpine

COPY entrypoint.sh .

WORKDIR /app

COPY requirements.txt .

RUN apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
    pip install -r requirements.txt --no-cache-dir

COPY . .

RUN pip install -e .

ENTRYPOINT ["/entrypoint.sh"]
