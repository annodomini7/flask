from requests import post, get, delete, put
import datetime

print(post('http://127.0.0.1:5000/data/5',
           json={"password": 'qwerty1234',
                 "data": [{
                     "barcode": 1,
                     "cost": 100,
                     "number": 1
                 },
                     {
                         "barcode": 2,
                         "cost": 100,
                         "number": 1
                     },
                     {
                         "barcode": 3,
                         "cost": 100,
                         "number": 1
                     }]}).json())

