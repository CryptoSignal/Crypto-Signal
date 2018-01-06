
import datetime
import structlog


from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    exchange = Column(String)
    base_symbol = Column(String)
    base_value = Column(Float)
    quote_symbol = Column(String)
    quote_value = Column(String)
    is_open = Column(Boolean)

    def __repr__(self):
        return "<Transaction(exchange='%s', timestamp='%s', purchased_symbol='%s', purchased_value='%s', sold_symbol='%s', sold_value='%s', is_open='%s')>" % (
            self.exchange,
            self.timestamp,
            self.base_symbol,
            self.base_value,
            self.quote_symbol,
            self.quote_value,
            self.is_open)


class DatabaseHandler():
    def __init__(self, database_config):
        connection_string = self.__create_connection_string(database_config)
        engine = create_engine(connection_string)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()


    def __create_connection_string(self, database_config):
        connection_string = database_config['engine'] + "://"
        if database_config['username'] and database_config['password']:
            connection_string += ':'.join([database_config['username'], database_config['password']])

        if database_config['host']:
            connection_string += '@' + database_config['host']

        if database_config['port']:
            connection_string += ':' + database_config['port']

        if database_config['db_name']:
            connection_string += '/' + database_config['db_name']

        return connection_string

    def get_transactions(self, filter_args={}):
        return self.session.query(Transaction).filter_by(**filter_args)
