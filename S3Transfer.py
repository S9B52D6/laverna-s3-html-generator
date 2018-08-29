import boto3
import psycopg2
import json
import os

#Sort list by DateTime descending, restrict to only {limit} newest objects
def sort_by_last_modified(_list, limit):
	_list.sort(key=lambda x: x.last_modified, reverse=True)
	for i in range(0, len(_list) - limit):
		_list.pop()
	return _list

def get_table_size(table, cursor):
	table_size_query = "SELECT COUNT(*) FROM {0}".format(table)
	cursor.execute(table_size_query)
	return cursor.fetchone()[0]

#Bucket returns cursor, need list to operate on
def build_list_from_bucket(bucket):
	list = []
	for obj in bucket.objects.all():
		list.append(obj)
	return list

#Load config variables
with open('config.json') as _file:
	config = json.load(_file)

BUCKET_NAME = config["bucketName"]
KEY_TABLE_NAME = config["tableNames"]["key"]
NOTEBOOK_TABLE_NAME = config["tableNames"]["notebook"]
CONNECTION_STRING = config["connectionString"]

#Connect to bucket
bucket = boto3.resource('s3').Bucket(BUCKET_NAME)
bucket_list = build_list_from_bucket(bucket)

key_insert_query = "INSERT INTO {} (key, size, storage_class, last_modified) VALUES (%s, %s, %s, %s);".format(KEY_TABLE_NAME)

sql_conn = psycopg2.connect(CONNECTION_STRING)
cursor = sql_conn.cursor()

#Determine if there are new items to insert into table
table_size = get_table_size(KEY_TABLE_NAME, cursor)
current_bucket_size = len(bucket_list)
num_new_items = current_bucket_size - table_size
has_new_version = num_new_items > 0

# if not has_new_version:
# 	exit()
#
# #Insert new items
# new_items = sort_by_last_modified(bucket_list, num_new_items)
# for obj in new_items:
# 	print obj.key
# 	iso_timestamp = obj.last_modified.strftime("%Y%m%dT%H%M%SZ")
# 	cursor.execute(key_insert_query, (obj.key, obj.size, obj.storage_class, iso_timestamp))
#
# sql_conn.commit()

select_latest_key_query = "SELECT key FROM {} ORDER BY last_modified DESC LIMIT 1".format(KEY_TABLE_NAME)
cursor.execute(select_latest_key_query)
key = cursor.fetchone()[0]

bucket.download_file(key, "archives/{}".format(key))
os.system("rm -drfv current/*")
os.system("unzip archives/{} -d current/".format(key))
os.chdir("current/laverna-backups/notes-db")

with open('notebooks.json') as _file:\
	notebooks = json.load(_file)

notebook_insert_query = "INSERT INTO {} (id, parent_id, name, count, created, updated) VALUES (%s, %s, %s, %s, to_timestamp(%s), to_timestamp(%s));".format(NOTEBOOK_TABLE_NAME)
notebook_insert_query_null = "INSERT INTO {} (id, parent_id, name, count, created, updated) VALUES (%s, NULL, %s, %s, to_timestamp(%s), to_timestamp(%s));".format(NOTEBOOK_TABLE_NAME)
for notebook in notebooks:
	print "INSERTING {}".format(notebook)
	if notebook["parentId"] == "0":
		cursor.execute(notebook_insert_query_null, (notebook["id"], notebook["name"], notebook["count"], notebook["created"], notebook["updated"]))
	else:
		cursor.execute(notebook_insert_query, (notebook["id"], notebook["parentId"], notebook["name"], notebook["count"], notebook["created"], notebook["updated"]))

sql_conn.commit()
cursor.close()
sql_conn.close()
