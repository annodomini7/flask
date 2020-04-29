import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Medicine(SqlAlchemyBase, UserMixin):
    __tablename__ = 'medicine'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    barcode = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    form = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    dose = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    marka = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    orm.relation("Data", back_populates='medicine')
    # user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    # user = orm.relation('User')
