FROM python:3.12.4

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

CMD ["python", "main.py"]