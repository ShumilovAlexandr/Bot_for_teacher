from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (Table,
                        MetaData,
                        Column,
                        Integer,
                        BigInteger,
                        String,
                        DateTime, TIME)

Base = declarative_base()


class Timesheet(Base):
    __tablename__ = 'timesheet'

    record_date = Column(DateTime)
    record_time = Column(TIME)
    fio = Column(String)
    chat_id = Column(Integer, primary_key=True, unique=True)
    user_id = Column(BigInteger)


class Timelist(Base):
    __tablename__ = 'timelist'

    id = Column(Integer, autoincrement=True, primary_key=True, unique=True)
    lesson_time = Column(TIME)