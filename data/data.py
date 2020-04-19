import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Data(SqlAlchemyBase, UserMixin):
    __tablename__ = 'data'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    cost = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    number = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    barcode = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("medicine.barcode"))
    pharmacy_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("pharmacy.id"))
    pharmacy = orm.relation('Pharmacy')
    medicine = orm.relation('Medicine')
