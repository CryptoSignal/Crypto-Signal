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

# numpy must be installed first for python TA-lib
RUN pip install numpy==1.14.0
RUN pip install -r requirements.txt

CMD ["/usr/local/bin/python","app.py"]
