FROM python:3.9-buster

WORKDIR /app/flask

ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_DEBUG=1
ENV FLASK_ENV=production

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

EXPOSE 4000

COPY . .

CMD ["flask", "run", "--port=4000"]
