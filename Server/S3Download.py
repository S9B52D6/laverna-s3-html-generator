import boto3
import psycopg2
import json
import os
import markdown
from datetime import datetime

from modules.bucket import Bucket
from modules.config import Config
from modules.keys import Keys
from modules.notebook import Notebook
from modules.note import Note

# Sort list by DateTime descending, restrict to only {limit} newest objects
def sortByLastModified(_list, limit):
    _list.sort(key=lambda x: x.last_modified, reverse=True)
    for i in range(0, len(_list) - limit):
        _list.pop()
    return _list

# Sort filenames in current directory into
# Dictionary organized by extension
def getFileNamesByExtension():
    fileDic = { }
    filenames = os.listdir('.')
    for name in filenames:
        extension = name.split('.')[1]
        if extension not in fileDic:
            fileDic[extension] = []
        fileDic[extension].append(name)
    return fileDic

# Create SQL connection
CONNECTION_STRING = Config().getConnectionString()
sql_conn = psycopg2.connect(CONNECTION_STRING)
cursor = sql_conn.cursor()

ROOT_PATH = Config().getRootPath()

# Determine if there are new items to insert into table
tableSize = Keys.getCount(cursor)
bucketSize = Bucket.getObjectCount(ROOT_PATH)
numNewItems = bucketSize - tableSize
hasNewVersion = numNewItems > 0

if not hasNewVersion:
    print "No New Version Available"
    print "Exiting..."
    exit()

# Insert new keys to database
bucketList = Bucket.getObjectsAsList(ROOT_PATH)
newItems = sortByLastModified(bucketList, numNewItems)
Keys.insertKeys(newItems, cursor)

print "{} new files uploaded since last update".format(numNewItems)

# Download latest file
key = Keys.getNewestKey(cursor)
print "Downloading file: [{}]...".format(key)
os.system("mkdir -p archives/laverna")
Bucket.getResource().download_file(key, "archives/{}".format(key))

# Delete old files
print "Deleting old files..."
os.system("mkdir -p current")
os.system("rm -drf current/*")

# Unzip archive
print "Unzipping archive..."
os.system("unzip -q archives/{} -d current/".format(key))
os.chdir("current/notes-db")

# Insert notebook metadata to database
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
    if note["notebookId"] != "0":
        notebookName = Notebook.getById(note["notebookId"], cursor)[2]
        os.system("mkdir -p ../../../../generated-files/{}".format(notebookName.replace(' ', '-')))
        outputFileName = "../../../../generated-files/{}/{}.html".format(notebookName, note["title"])
    else:
        outputFileName = "../../../../generated-files/{}.html".format(note["title"])

    outputFileName = outputFileName.replace(' ', '-')
    inputFileName = "{}.md".format(note["id"])
    markdown.markdownFromFile(inputFileName, outputFileName)

sql_conn.commit()
cursor.close()
sql_conn.close()

print "Finished: {} new files generated".format(len(notesNeedingGeneration))
