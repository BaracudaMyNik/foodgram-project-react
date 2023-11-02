FROM python:3.7-slim

WORKDIR /app

pip install gunicorn==20.1.0

COPY requirements.txt /app

RUN python -m pip install --upgrade pip

RUN pip3 install -r /app/requirements.txt --no-cache-dir

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "backend.wsgi:application"]
