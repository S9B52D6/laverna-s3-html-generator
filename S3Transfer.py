import boto3
import psycopg2
import json
import os
from datetime import datetime
from bucket import Bucket
from config import Config
from keys import Keys
from notebook import Notebook
from note import Note

#Sort list by DateTime descending, restrict to only {limit} newest objects
def sortByLastModified(_list, limit):
	_list.sort(key=lambda x: x.last_modified, reverse=True)
	for i in range(0, len(_list) - limit):
		_list.pop()
	return _list

def getFileNamesByExtension():
	fileDic = { }
	filenames = os.listdir('.')
	for name in filenames:
		extension = name.split('.')[1]
		if extension not in fileDic:
			fileDic[extension] = []
		fileDic[extension].append(name)
	return fileDic

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

# Bucket.getResource().download_file(key, "archives/{}".format(key))
# os.system("rm -drfv current/*")
# os.system("unzip archives/{} -d current/".format(key))
os.chdir("current/laverna-backups/notes-db")

# with open('notebooks.json') as _file:
# 	notebooks = json.load(_file)
#
# Notebook.insertNotebooks(notebooks, cursor)

os.chdir('notes')

filenames = getFileNamesByExtension()
for name in filenames["json"]:
	id = name.split('.')[0]
	note = json.load(open(name))

	if not Note.hasId(id, cursor):
		Note.insert(note, cursor)
	else:
		dbRowDate = Note.getById(id)[3]
		fileDate = datetime.fromtimestamp(note["updated"] / 1000)
		if dbRowDate < fileDate:
			Note.updateById(note, cursor)

sql_conn.commit()
cursor.close()
sql_conn.close()
