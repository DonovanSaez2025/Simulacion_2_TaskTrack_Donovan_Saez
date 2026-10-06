# Importaciones
import os
import pymysql.cursors

# Clase para conectarse a la base de datos
class MySQLConnection:
    # Método constructor
    def __init__(self):
        self.connection = pymysql.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True)

    # Método para intentar conectarse a la base de datos
    def query_db(self, query, data=None):
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(query, data)
                if query.lower().startswith("insert"):
                    return cursor.lastrowid
                elif query.lower().startswith("select"):
                    return cursor.fetchall()
                else:
                    return cursor.rowcount
            except Exception as e:
                print(f"Error en la consulta SQL: {e}")
                return False
            finally:
                self.connection.close()

def connectToMySQL():
    return MySQLConnection()