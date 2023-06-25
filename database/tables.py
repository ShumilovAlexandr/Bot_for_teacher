from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (Table,
                        MetaData,
                        Column,
                        Integer,
                        String,
                        DateTime, TIME)

Base = declarative_base()


class Timesheet(Base):
    __tablename__ = 'timesheet'

    record_date = Column(DateTime)
    record_time = Column(TIME)
    fio = Column(String)
    user_id = Column(Integer, primary_key=True, unique=True)
