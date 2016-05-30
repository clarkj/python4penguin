#!/usr/bin/python
from pymongo import MongoClient
from datetime import datetime

# establish a connection to the database
client = MongoClient()
# selecting a paticular database table
db = client.test2

cursor = db.josh5.find()

for document in cursor:
	print(document)