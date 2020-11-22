FROM python:3.8-buster

# TA-lib is required by the python TA-lib wrapper. This provides analysis.
COPY lib/ta-lib-0.4.0-src.tar.gz /tmp/ta-lib-0.4.0-src.tar.gz

RUN cd /tmp && \
  tar -xvzf ta-lib-0.4.0-src.tar.gz && \
  cd ta-lib/ && \
  ./configure --prefix=/usr && \
  make && \
  make install

ADD app/requirements-step-1.txt /app/requirements-step-1.txt
ADD app/requirements-step-2.txt /app/requirements-step-2.txt
WORKDIR /app

# Pip doesn't install requirements sequentially.
# To ensure pre-reqs are installed in the correct
# order they have been split into two files
RUN pip install -r requirements-step-1.txt
RUN pip install -r requirements-step-2.txt

CMD ["python","app.py"]
