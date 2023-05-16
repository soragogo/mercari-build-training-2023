FROM python:3.10.6-alpine

RUN addgroup -S mercari && adduser -S trainee -G mercari
#RUN chown -R trainee:mercari /path/to/db

USER root

RUN apk add --update --no-cache python3 py3-pip

WORKDIR /app
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
RUN mkdir -p /app/db \
    && mkdir -p /app/images 

COPY ../db db
COPY main.py .
COPY images images

RUN chown -R trainee:mercari /app/db

USER trainee

CMD ["python", "-V"]
