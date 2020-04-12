from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument('phone', required=False)
parser.add_argument('hours', required=False)
parser.add_argument('address', required=True)
parser.add_argument('hashed_password', required=True)
parser.add_argument('city', required=True)
parser.add_argument('name', required=True)
parser.add_argument('id', required=True, type=int)
