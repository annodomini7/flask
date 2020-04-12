from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument('number', required=True, type=int)
parser.add_argument('cost', required=True, type=float)
parser.add_argument('id', required=True, type=int)
parser.add_argument('medicine_id', required=True, type=int)
parser.add_argument('pharmacy_id', required=True, type=int)
