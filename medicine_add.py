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
from data.data import Data

with open('ostatki.csv', encoding="windows-1251") as csvfile:
    reader = csv.DictReader(csvfile, delimiter=';', quotechar='"')
    db_session.global_init("db/pharmacy.db")
    session = db_session.create_session()
    for el in reader:
        # print(, ,, , )
        user = Data()
        user.barcode = el['BARCODE']
        user.pharmacy_id = el['APTEKA']
        user.cost = el['CENA']
        user.number = el['OST']
        session.add(user)
        session.commit()
