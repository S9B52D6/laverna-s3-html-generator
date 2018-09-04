import json

class Config:
    filepath = "config.json"
    data = json.load(open(filepath))

    @staticmethod
    def getConnectionString():
        return Config.data["connectionString"]

    @staticmethod
    def getBucketName():
        return Config.data["aws"]["bucketName"]

    @staticmethod
    def getTableNames():
        return Config.data["tableNames"]

    @staticmethod
    def getRootPath():
        return Config.data["aws"]["rootPath"]
