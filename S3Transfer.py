import boto3
import psycopg2
import json
import os
import markdown
from datetime import datetime

from bucket import Bucket
from config import Config
from keys import Keys
from notebook import Notebook
from note import Note

# Sort list by DateTime descending, restrict to only {limit} newest objects
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

# Connect to bucket
bucket_list = Bucket.getObjectsAsList()

# Create SQL connection
sql_conn = psycopg2.connect(CONNECTION_STRING)
cursor = sql_conn.cursor()

# Determine if there are new items to insert into table
table_size = Keys.getCount(cursor)
current_bucket_size = Bucket.getObjectCount()
num_new_items = current_bucket_size - table_size
has_new_version = num_new_items > 0

if not has_new_version:
	print "No New Version Available"
	print "Exiting..."
	exit()

# Insert new keys to database
new_items = sortByLastModified(bucket_list, num_new_items)
Keys.insertKeys(new_items, cursor)

print "{} new files uploaded since last update".format(num_new_items)

# Unzip latest backup
key = Keys.getNewestKey(cursor)
print "Downloading file: [{}]...".format(key)
Bucket.getResource().download_file(key, "archives/{}".format(key))
print "Deleting old files..."
os.system("rm -drf current/*")
print "Unzipping archive..."
os.system("unzip -q archives/{} -d current/".format(key))
os.chdir("current/laverna-backups/notes-db")

# Insert notebook metadeta to database
with open('notebooks.json') as _file:
	notebooks = json.load(_file)
Notebook.insert(notebooks, cursor)

os.chdir('notes')

# Ids for notes which need to have their
# markdown converted into html
notesNeedingGeneration = []

print("Updating note metadata...")

filenames = getFileNamesByExtension()
for name in filenames["json"]:
	id = name.split('.')[0]
	note = json.load(open(name))

	if not Note.hasId(id, cursor):
		Note.insert(note, cursor)
		notesNeedingGeneration.append(note)
	else:
		dbRowDate = Note.getById(id, cursor)[3]
		fileDate = datetime.fromtimestamp(note["updated"] / 1000)
		if dbRowDate < fileDate:
			Note.updateById(note, cursor)
			notesNeedingGeneration.append(note)


print "Generating HTML files..."

# Generate HTML from markdown files, write to generated-files/
for note in notesNeedingGeneration:
	# Create sub-directory with name of each notebook
	notebookName = Notebook.getById(note["notebookId"], cursor)[2].replace(' ', '-')
	os.system("mkdir -p ../../../../generated-files/{}".format(notebookName))

	inputFileName = "{}.md".format(note["id"])
	outputFileName = "../../../../generated-files/{}/{}.html".format(notebookName, note["id"])
	markdown.markdownFromFile(inputFileName, outputFileName)

sql_conn.commit()
cursor.close()
sql_conn.close()

print "Finished: {} new files generated".format(len(notesNeedingGeneration))
