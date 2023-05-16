FROM alpine

RUN addgroup -S mercari && adduser -S trainee -G mercari
#RUN chown -R trainee:mercari /path/to/db

USER root

RUN apk add --update --no-cache python3 py3-pip

WORKDIR /app
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . /app

COPY ../db db
COPY main.py .

RUN chown -R trainee:mercari /app/db

USER trainee
CMD ["python", "app.py"]

