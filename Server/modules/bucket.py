from config import Config
import boto3

class Bucket:
    BUCKET_NAME = Config.getBucketName()

    @staticmethod
    def getResource():
        return boto3.resource('s3').Bucket(Bucket.BUCKET_NAME)

    @staticmethod
    def getObjectsAsList():
        list = []
        for obj in Bucket.getResource().objects.all():
            list.append(obj)
        return list

    @staticmethod
    def getObjectsAsList(rootPath):
        list = []
        for obj in Bucket.getResource().objects.all():
            if rootPath in obj.key:
                list.append(obj)
        return list

    @staticmethod
    def getObjectCount():
        return len(Bucket.getObjectsAsList())

    @staticmethod
    def getObjectCount(rootPath):
        return len(Bucket.getObjectsAsList(rootPath))
