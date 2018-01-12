
from datetime import datetime

import structlog

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Holdings(Base):
    __tablename__ = 'holdings'

    id = Column(Integer, primary_key=True)
    create_time = Column(DateTime, default=datetime.now())
    update_time = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    exchange = Column(String)
    symbol = Column(String)
    volume_free = Column(Float)
    volume_used = Column(Float)
    volume_total = Column(Float)

    def __repr__(self):
        return "<Holdings(\
            exchange='%s',\
            create_time='%s',\
            update_time='%s',\
            symbol='%s',\
            volume_free='%s',\
            volume_used='%s',\
            volume_total='%s')>" % (
                self.exchange,
                self.create_time,
                self.update_time,
                self.symbol,
                self.volume_free,
                self.volume_used,
                self.volume_total
            )

class Transactions(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    create_time = Column(DateTime, default=datetime.now())
    update_time = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    exchange = Column(String)
    base_symbol = Column(String)
    quote_symbol = Column(String)
    action = Column(String)
    base_value = Column(Float)
    quote_value = Column(Float)
    fee_rate = Column(Float)
    base_volume = Column(Float)
    quote_volume = Column(Float)

    def __repr__(self):
        return "<Transactions(\
            exchange='%s',\
            create_time='%s',\
            update_time='%s',\
            base_symbol='%s',\
            quote_symbol='%s',\
            action='%s',\
            base_value='%s',\
            quote_value='%s',\
            fee_rate='%s',\
            base_volume='%s',\
            quote_volume='%s')>" % (
                self.exchange,
                self.create_time,
                self.update_time,
                self.base_symbol,
                self.quote_symbol,
                self.action,
                self.base_value,
                self.quote_value,
                self.fee_rate,
                self.base_volume,
                self.quote_volume
            )


class DatabaseHandler():
    def __init__(self, database_config):
        connection_string = self.__create_connection_string(database_config)
        engine = create_engine(connection_string)
        Base.metadata.create_all(engine)
        session = sessionmaker(bind=engine)
        self.session = session()
        self.logger = structlog.get_logger()


    def __create_connection_string(self, database_config):
        connection_string = database_config['engine'] + "://"
        if database_config['username'] and database_config['password']:
            connection_string += ':'.join([
                database_config['username'],
                database_config['password']])

        if database_config['host']:
            connection_string += '@' + database_config['host']

        if database_config['port']:
            connection_string += ':' + database_config['port']

        if database_config['db_name']:
            connection_string += '/' + database_config['db_name']

        return connection_string

    def read_holdings(self, filter_args={}):
        return self.session.query(Holdings).filter_by(**filter_args)

    def create_holding(self, create_args={}):
        create_success = True
        try:
            self.session.add(Holdings(**create_args))
            self.session.commit()
        except SQLAlchemyError:
            create_success = False
            self.logger.error("Failed to create holding record!", create_args=create_args)
            self.session.rollback()
        return create_success

    def update_holding(self, holding, update_args={}):
        update_success = True
        try:
            self.session.query(Holdings).filter_by(id=holding.id).update(update_args)
            self.session.commit()
        except SQLAlchemyError:
            update_success = False
            self.logger.error("Failed to update holding record!", update_args=update_args)
            self.session.rollback()
        return update_success

    def read_transactions(self, filter_args={}):
        return self.session.query(Transactions).filter_by(**filter_args)

    def create_transaction(self, create_args={}):
        create_success = True
        try:
            self.session.add(Transactions(**create_args))
            self.session.commit()
        except SQLAlchemyError:
            create_success = False
            self.logger.error("Failed to create transaction record!", create_args=create_args)
            self.session.rollback()
        return create_success

    def update_transaction(self, transaction, update_args={}):
        update_success = True
        try:
            self.session.query(Transactions).filter_by(id=transaction.id).update(update_args)
            self.session.commit()
        except SQLAlchemyError:
            update_success = False
            self.logger.error("Failed to update transaction record!", update_args=update_args)
            self.session.rollback()
        return update_success
