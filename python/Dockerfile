FROM python:3.10.6-alpine

RUN addgroup -S mercari && adduser -S trainee -G mercari


USER root


WORKDIR /app
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
RUN mkdir -p /app/db \
    && mkdir -p /app/images 

COPY db db
COPY main.py .
COPY images images

RUN chown -R trainee:mercari /app/db \
    && chown -R trainee:mercari /app/images 
USER trainee


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"]