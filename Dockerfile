FROM python:latest

# TA-lib is required by the python TA-lib wrapper. This provides analysis.
COPY lib/ta-lib-0.4.0-src.tar.gz /tmp/ta-lib-0.4.0-src.tar.gz

RUN cd /tmp && \
  tar -xvzf ta-lib-0.4.0-src.tar.gz && \
  cd ta-lib/ && \
  ./configure --prefix=/usr && \
  make && \
  make install

COPY ./app /app

WORKDIR /app

RUN pip install --upgrade pip
RUN pip install -r requirements-step-1.txt
RUN pip install -r requirements-step-2.txt

CMD ["python","app.py"]
