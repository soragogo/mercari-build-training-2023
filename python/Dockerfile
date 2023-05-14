FROM python:3.9.6-alphine

RUN addgroup -S mercari && adduser -S trainee -G mercari

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt

USER trainee
CMD ["python", "app.py"]

