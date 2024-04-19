import datetime
from time import sleep
from typing import Union

from openpyxl import load_workbook
from sqlalchemy.sql.functions import random
from sqlalchemy.sql.operators import or_

from config import logger, engine_kwargs, project_name, smtp_host, smtp_author, ip_address, robot_name
from tools.smtp import smtp_send

from sqlalchemy import create_engine, Column, Integer, String, DateTime, MetaData, Table, Date, Boolean, select, Float
from sqlalchemy.orm import declarative_base, sessionmaker, Session

Base = declarative_base()


class Table_(Base):
    __tablename__ = robot_name.replace('-', '_')

    date_created = Column(DateTime, default=None)
    date_started = Column(DateTime, default=None)
    date_edited = Column(DateTime, default=None)
    executor_name = Column(String(512), default=None)
    status = Column(String(64), default=None)
    skillaz_status = Column(String(512), default=None)
    skillaz_action = Column(String(512), default=None)
    previous_status = Column(String(512), default=None)
    error_reason = Column(String(512), default=None)
    response_date = Column(DateTime, default=None)
    city = Column(String(512), default=None)
    job = Column(String(512), default=None)
    first_name = Column(String(512), default=None)
    last_name = Column(String(512), default=None)
    phone_number = Column(String(512), default=None, primary_key=True)

    @property
    def dict(self):
        m = self.__dict__.copy()
        return m


def add_to_db(session: Session, status_: str, skillaz_status_: str or None, skillaz_action_: str or None, response_date_: datetime, city_: str, job_: str, first_name_: str or None, last_name_: str or None,
              phone_number_: str):

    if session.query(Table_).filter(phone_number_ == Table_.phone_number).scalar() is None or len(phone_number_) != 10:
        session.add(Table_(
            date_created=datetime.datetime.now(),
            date_started=None,
            date_edited=None,
            executor_name=ip_address if status_ != 'new' else None,
            status=status_,
            skillaz_status=skillaz_status_,
            skillaz_action=skillaz_action_,
            response_date=response_date_,
            city=city_,
            job=job_,
            first_name=first_name_,
            last_name=last_name_,
            phone_number=phone_number_
        ))

        session.commit()


def get_all_data(session: Session):

    rows = [row for row in session.query(Table_).all()]

    print(type(rows[0]))

    return rows


def get_all_data_by_status(session: Session, status: Union[list, str]):

    if isinstance(status, list):
        rows = [row for row in session.query(Table_).filter(Table_.skillaz_status.in_(status))
        .filter(or_(Table_.executor_name == ip_address, Table_.executor_name == None)).order_by(random()).all()]

        # for i in [row for row in session.query(Table_).filter(Table_.executor_name == None).all()]:
        #     print(type(i.executor_name))
    else:
        rows = [row for row in session.query(Table_).filter(status == Table_.skillaz_status
                                                            )
        .filter(or_(Table_.executor_name == ip_address, Table_.executor_name == None)).order_by(random()).all()]

    return list(rows)


def update_in_db(session: Session, row: Table_, status_: str, skillaz_status_: str, skillaz_action_: str or None, previous_status_: str or None, error_reason_: str or None, response_date_: datetime, city_: str, job_: str,
                 first_name_: str, last_name_: str, phone_number_: str):

    row.date_edited = datetime.datetime.now()
    row.date_started = datetime.datetime.now() if row.date_started is None else row.date_started
    row.executor_name = ip_address

    row.status = status_
    row.error_reason = error_reason_
    row.skillaz_status = skillaz_status_
    row.skillaz_action = skillaz_action_
    row.previous_status = previous_status_

    row.response_date = response_date_,
    row.city = city_,
    row.job = job_,
    row.first_name = first_name_,
    row.last_name = last_name_,
    row.phone_number = phone_number_,

    session.commit()


