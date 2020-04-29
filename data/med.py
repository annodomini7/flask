import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Med(SqlAlchemyBase, UserMixin):
    __tablename__ = 'med'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    barcode = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    cost = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    num = sqlalchemy.Column(sqlalchemy.String, nullable=False)
