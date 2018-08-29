from config import Config

class Notebook:
    NOTEBOOK_TABLE_NAME = Config.getTableNames()["notebook"]

    @staticmethod
    def insert(json, cursor):
        query = """INSERT INTO {}
                   (id, parent_id, name, count, created, updated)
                   VALUES (%s, %s, %s, %s, to_timestamp(%s), to_timestamp(%s));
                """.format(Notebook.NOTEBOOK_TABLE_NAME)

        null_query = """INSERT INTO {}
                        (id, parent_id, name, count, created, updated)
                        VALUES (%s, NULL, %s, %s, to_timestamp(%s), to_timestamp(%s));
                     """.format(Notebook.NOTEBOOK_TABLE_NAME)

        for notebook in json:
        	print "INSERTING {}".format(notebook)
        	if notebook["parentId"] == "0":
        		cursor.execute(null_query, (notebook["id"], notebook["name"], notebook["count"],
                               notebook["created"], notebook["updated"]))
        	else:
        		cursor.execute(query, (notebook["id"], notebook["parentId"], notebook["name"],
                               notebook["count"], notebook["created"], notebook["updated"]))
