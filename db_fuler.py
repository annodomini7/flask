import sys
import requests
from data import db_session
from data.pharmacy import Pharmacy


def x():
    search_api_server = "https://search-maps.yandex.ru/v1/"
    api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"

    search_params = {
        "apikey": api_key,
        "text": "аптека",
        "lang": "ru_RU",
        "ll": ",".join([toponym_longitude, toponym_lattitude]),
        "type": "biz"
    }

    response = requests.get(search_api_server, params=search_params)
    # print(response.url)
    if not response:
        # ...
        pass

    # Преобразуем ответ в json-объект
    json_response = response.json()

    for i in range(10):
        organization = json_response["features"][i]
        name = organization["properties"]["CompanyMetaData"]["name"]
        address = organization["properties"]["CompanyMetaData"]["address"]
        try:
            hours = organization["properties"]["CompanyMetaData"]["Hours"]["text"]
        except Exception:
            hours = None
        try:
            phone = organization["properties"]["CompanyMetaData"]["Phones"][0]["formatted"]
        except Exception:
            phone = None
        user = Pharmacy()
        user.name = name
        user.city = toponym_to_find
        user.address = address
        user.hours = hours
        user.phone = phone
        user.set_password("qwerty123")
        session.add(user)
        session.commit()


city = ['Зеленокумск']
for toponym_to_find in city:
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

    geocoder_params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": toponym_to_find,
        "format": "json"}

    response = requests.get(geocoder_api_server, params=geocoder_params)

    if not response:
        pass

    json_response = response.json()
    toponym = json_response["response"]["GeoObjectCollection"][
        "featureMember"][0]["GeoObject"]
    toponym_coodrinates = toponym["Point"]["pos"]
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
    db_session.global_init("db/pharmacy.db")
    session = db_session.create_session()
    x()
