from config import Config
import boto3

class Keys:
    KEY_TABLE_NAME = Config().getTableNames()["key"]

    @staticmethod
    def getCount(cursor):
        query = "SELECT COUNT(*) FROM {}".format(Keys.KEY_TABLE_NAME)
    	cursor.execute(query)
    	return cursor.fetchone()[0]

    @staticmethod
    def insertKeys(keys, cursor):
        query = """INSERT INTO {}
                   (key, size, storage_class, last_modified)
                   VALUES (%s, %s, %s, %s);
                """.format(Keys.KEY_TABLE_NAME)

        for key in keys:
            print obj.key
            iso_timestamp = obj.last_modified.strftime("%Y%m%dT%H%M%SZ")
            cursor.execute(query,
                           (obj.key, obj.size, obj.storage_class, iso_timestamp))

    @staticmethod
    def getNewestKey(cursor):
        query = """SELECT key FROM {}
                   ORDER BY last_modified DESC LIMIT 1
                """.format(Keys.KEY_TABLE_NAME)

        cursor.execute(query)
        return cursor.fetchone()[0]
