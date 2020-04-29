# from requests import post, get, delete, put
# import datetime
#
# print(post('http://127.0.0.1:5000/data/5',
#            json={"password": 'qwerty1234',
#                  "data": [{
#                      "barcode": 1,
#                      "cost": 100,
#                      "number": 1
#                  },
#                      {
#                          "barcode": 2,
#                          "cost": 100,
#                          "number": 1
#                      },
#                      {
#                          "barcode": 3,
#                          "cost": 100,
#                          "number": 1
#                      }]}).json())
#
# import csv
# from data import db_session
# from data.medicine import Medicine
#
# with open('tovar.csv', encoding="windows-1251") as csvfile:
#     reader = csv.DictReader(csvfile, delimiter=';', quotechar='"')
#     db_session.global_init("db/pharmacy.db")
#     session = db_session.create_session()
#     for el in reader:
#         # print(, ,, , )
#         user = Medicine()
#         user.barcode = el['BARCODE']
#         user.name = el['NAZV']
#         user.form = el['FORMA']
#         user.dose = el['DOZ']
#         user.marka = el['MAKER']
#         session.add(user)
#         session.commit()
import csv
from data import db_session
from data.med import Med
from random import shuffle, randint
from data.data import Data

db_session.global_init("db/pharmacy.db")
session = db_session.create_session()
for el in session.query(Data).filter(Data.pharmacy_id == 1):
    print(el.barcode)

