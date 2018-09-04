from config import Config

class Notebook:
    NOTEBOOK_TABLE_NAME = Config.getTableNames()["notebook"]

    @staticmethod
    def insert(json, cursor):
        query = """INSERT INTO {}
                   (id, parent_id, name, count, created, updated)
                   VALUES (%s, %s, %s, %s, to_timestamp(%s), to_timestamp(%s))
                   ON CONFLICT (id) DO NOTHING;""".format(Notebook.NOTEBOOK_TABLE_NAME)

        null_query = """INSERT INTO {}
                        (id, parent_id, name, count, created, updated)
                        VALUES (%s, NULL, %s, %s, to_timestamp(%s), to_timestamp(%s))
                        ON CONFLICT (id) DO NOTHING;""".format(Notebook.NOTEBOOK_TABLE_NAME)

        for notebook in json:
            if notebook["parentId"] == "0":
                cursor.execute(null_query, (notebook["id"], notebook["name"], notebook["count"],
                               notebook["created"], notebook["updated"]))
            else:
                cursor.execute(query, (notebook["id"], notebook["parentId"], notebook["name"],
                               notebook["count"], notebook["created"], notebook["updated"]))

    @staticmethod
    def getById(id, cursor):
        query = """SELECT id, parent_id, name, count, created, updated
                   FROM {} WHERE id = %s;""".format(Notebook.NOTEBOOK_TABLE_NAME)
        cursor.execute(query, (id,))
        return cursor.fetchone()
