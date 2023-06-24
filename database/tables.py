from sqlalchemy import (Table,
                        MetaData,
                        Column,
                        Integer,
                        String,
                        DateTime, TIME)

metadata = MetaData()

timesheet = Table(
    'timesheet',
    metadata,
    Column('record_date', DateTime),
    Column('record_time', TIME),
    Column('fio', String),
    Column('user_id', Integer, primary_key=True, unique=True)
)
