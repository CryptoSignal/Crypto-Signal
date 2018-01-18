FROM python:3.6

RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
  tar -xvzf ta-lib-0.4.0-src.tar.gz && \
  cd ta-lib/ && \
  ./configure --prefix=/usr && \
  make && \
  make install

ADD app/ /app
WORKDIR /app

# numpy must be installed first for python ta-lib
RUN pip install numpy==1.14.0
RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["/usr/local/bin/python","app.py"]
