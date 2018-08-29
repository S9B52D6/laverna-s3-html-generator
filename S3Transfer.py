import boto3
import psycopg2
import json
import os
from bucket import Bucket
from config import Config
from keys import Keys
from notebook import Notebook

#Sort list by DateTime descending, restrict to only {limit} newest objects
def sortByLastModified(_list, limit):
	_list.sort(key=lambda x: x.last_modified, reverse=True)
	for i in range(0, len(_list) - limit):
		_list.pop()
	return _list

CONNECTION_STRING = Config().getConnectionString()

#Connect to bucket
bucket_list = Bucket.getObjectsAsList()

#Create SQL connection
sql_conn = psycopg2.connect(CONNECTION_STRING)
cursor = sql_conn.cursor()

#Determine if there are new items to insert into table
table_size = Keys.getCount(cursor)
current_bucket_size = Bucket.getObjectCount()
num_new_items = current_bucket_size - table_size
has_new_version = num_new_items > 0

# if not has_new_version:
# 	exit()
#
# #Insert new items
# new_items = sortByLastModified(bucket_list, num_new_items)
# Keys.insertKeys(new_items, cursor)

key = Keys.getNewestKey(cursor)

Bucket.getResource().download_file(key, "archives/{}".format(key))
os.system("rm -drfv current/*")
os.system("unzip archives/{} -d current/".format(key))
os.chdir("current/laverna-backups/notes-db")

with open('notebooks.json') as _file:
	notebooks = json.load(_file)

Notebook.insertNotebooks(notebooks, cursor)

sql_conn.commit()
cursor.close()
sql_conn.close()
