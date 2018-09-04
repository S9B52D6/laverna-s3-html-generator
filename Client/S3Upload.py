import datetime as DateTime
import boto3 as boto3
import os as os
from modules.config import Config

currentDateTime = DateTime.datetime.now().isoformat()
ROOT_PATH = Config().getRootPath()
zipName = "laverna-{}.zip".format(currentDateTime)
zipFilePath = "archives/{}".format(zipName)
key = "{}{}".format(ROOT_PATH, zipName)

syncDirectory = Config().getSyncDirectory()
print "Creating archive from Laverna data..."
os.system("mkdir -p archives/")
os.system("zip -rq {} {}".format(zipFilePath, syncDirectory))

s3 = boto3.client('s3')
bucketName = Config().getBucketName()
print "Uploading archive to AWS-S3..."
with open(zipFilePath, 'rb') as archive:
    s3.upload_fileobj(archive, bucketName, key)
