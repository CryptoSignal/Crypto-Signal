"""Class for use with the sqlalchemy ORM. Contains users transactions.
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime

from db.base import BASE

class Transactions(BASE):
    """Class for use with the sqlalchemy ORM. Contains users transactions.
    """

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
