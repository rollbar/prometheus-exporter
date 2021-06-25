FROM python:3.8

WORKDIR /app
COPY requirements.txt .
COPY metrics/*.py .

RUN pip install -r requirements.txt
CMD ["python", "./app.py"]
