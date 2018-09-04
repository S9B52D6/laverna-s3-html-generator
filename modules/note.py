from config import Config

class Note:
    NOTE_TABLE_NAME = Config.getTableNames()["notes"]

    @staticmethod
    def insert(json, cursor):
        query = """INSERT INTO {} (id, title, created, updated, notebook_id, is_favorite)
                   VALUES (%s, %s, to_timestamp(%s), to_timestamp(%s), %s, %s)""".format(Note.NOTE_TABLE_NAME)

        null_query = """INSERT INTO {} (id, title, created, updated, is_favorite)
                        VALUES(%s, %s, to_timestamp(%s), to_timestamp(%s), %s)""".format(Note.NOTE_TABLE_NAME)

        if json["notebookId"] == "0":
            cursor.execute(null_query, (json["id"], json["title"],
                                        json["created"], json["updated"], bool(json["isFavorite"])))
        else:
            cursor.execute(query, (json["id"], json["title"], json["created"],
                                   json["updated"], json["notebookId"], bool(json["isFavorite"])))

    @staticmethod
    def hasId(id, cursor):
        query = "SELECT COUNT(1) FROM {} WHERE id = %s;".format(Note.NOTE_TABLE_NAME)
        cursor.execute(query, (id,))
        return cursor.fetchone()[0] > 0

    @staticmethod
    def getById(id, cursor):
        query = """SELECT id, title, created, updated, notebook_id, is_favorite FROM {}
                   WHERE id = %s;""".format(Note.NOTE_TABLE_NAME)
        cursor.execute(query, (id,))
        return cursor.fetchone()

    @staticmethod
    def updateById(json, cursor):
        query = """UPDATE {} SET title = %s, updated = to_timestamp(%s), notebook_id = %s, is_favorite = %s
                   WHERE id = %s""".format(Note.NOTE_TABLE_NAME)
        cursor.execute(query, (json["title"], json["updated"], json["notebookId"],
                               bool(json["isFavorite"]), json["id"]))
