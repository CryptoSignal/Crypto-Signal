FROM python:3.6

ADD app/ /app
WORKDIR /app

RUN pip install -r requirements.txt

CMD ["/usr/local/bin/python","app.py"]