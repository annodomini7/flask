from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument('dose', required=True)
parser.add_argument('form', required=True)
parser.add_argument('name', required=True)
parser.add_argument('id', required=True, type=int)
