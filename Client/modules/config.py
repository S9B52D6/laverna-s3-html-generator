import json

class Config:
    filepath = "config.json"
    data = json.load(open(filepath))

    @staticmethod
    def getBucketName():
        return Config.data["aws"]["bucketName"]

    @staticmethod
    def getRootPath():
        return Config.data["aws"]["rootPath"]

    @staticmethod
    def getSyncDirectory():
        return Config.data["client"]["syncDirectory"]

    @staticmethod
    def getSyncDirectoryParent():
        return Config.data["client"]["syncDirectoryParent"]
