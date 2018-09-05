import datetime as DateTime
import boto3 as boto3
import os as os
from modules.config import Config

currentDateTime = DateTime.datetime.now().isoformat()
ROOT_PATH = Config().getRootPath()
zipName = "laverna-{}.zip".format(currentDateTime)
zipFilePath = "{}".format(zipName)
key = "{}{}".format(ROOT_PATH, zipName)

print DateTime.datetime.now()

syncDirectory = Config().getSyncDirectory()
syncDirectoryParent = Config().getSyncDirectoryParent()
print "Creating archive from Laverna data..."
os.chdir(syncDirectoryParent)
os.system("zip -rq {} {}".format(zipFilePath, syncDirectory))

s3 = boto3.client('s3')
bucketName = Config().getBucketName()
print "Uploading archive to AWS-S3..."
with open(zipFilePath, 'rb') as archive:
    s3.upload_fileobj(archive, bucketName, key)
