FROM python:3.6-jessie

# TA-lib is required by the python TA-lib wrapper. This provides analysis.
COPY lib/ta-lib-0.4.0-src.tar.gz /tmp/ta-lib-0.4.0-src.tar.gz

RUN cd /tmp && \
  tar -xvzf ta-lib-0.4.0-src.tar.gz && \
  cd ta-lib/ && \
  ./configure --prefix=/usr && \
  make && \
  make install

ADD app/ /app
WORKDIR /app

# Pip doesn't install requirements sequentially.
# To ensure pre-reqs are installed in the correct
# order they have been split into two files
RUN pip install -r requirements-step-1.txt
RUN pip install -r requirements-step-2.txt

CMD ["/usr/local/bin/python","app.py"]
