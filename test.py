# # from requests import post, get, delete, put
# # import datetime
# #
# # print(post('http://127.0.0.1:5000/data/5',
# #            json={"password": 'qwerty1234',
# #                  "data": [{
# #                      "barcode": 1,
# #                      "cost": 100,
# #                      "number": 1
# #                  },
# #                      {
# #                          "barcode": 2,
# #                          "cost": 100,
# #                          "number": 1
# #                      },
# #                      {
# #                          "barcode": 3,
# #                          "cost": 100,
# #                          "number": 1
# #                      }]}).json())
# #
# # import csv
# # from data import db_session
# # from data.medicine import Medicine
# #
# # with open('tovar.csv', encoding="windows-1251") as csvfile:
# #     reader = csv.DictReader(csvfile, delimiter=';', quotechar='"')
# #     db_session.global_init("db/pharmacy.db")
# #     session = db_session.create_session()
# #     for el in reader:
# #         # print(, ,, , )
# #         user = Medicine()
# #         user.barcode = el['BARCODE']
# #         user.name = el['NAZV']
# #         user.form = el['FORMA']
# #         user.dose = el['DOZ']
# #         user.marka = el['MAKER']
# #         session.add(user)
# #         session.commit()
# import csv
# from data import db_session
# from data.med import Med
# from random import shuffle, randint
# from data.data import Data
#
# db_session.global_init("db/pharmacy.db")
# session = db_session.create_session()
# for el in session.query(Data).filter(Data.pharmacy_id == 1):
#     print(el.barcode)
#
import requests


def x():
    ad = "+".join(input().split())
    geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode" \
                       f"={ad}&format=json"

    response = requests.get(geocoder_request)
    print()
    if response:
        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        toponym_coodrinates = toponym["Point"]["pos"]
        return toponym_coodrinates
    else:
        pass


#
# search_api_server = "https://search-maps.yandex.ru/v1/"
# api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"

address_ll = ",".join(x().split())
geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode" \
                   f"={address_ll}&format=json&kind=district"

response = requests.get(geocoder_request)
if response:
    json_response = response.json()
    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["name"]
    print(toponym)
