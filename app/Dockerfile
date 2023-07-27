FROM python:3.8

RUN apt-get update && apt-get install -y libgl1-mesa-glx

WORKDIR /app

ADD . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "app:app"]