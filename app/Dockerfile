# docker run --rm -d -v "/c/projects/eks/irsademo/credentials:/root/.aws/credentials" s3time
FROM python:3.6-slim

WORKDIR /app
ADD requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY app.py /app/app.py

CMD ["python", "app.py"]