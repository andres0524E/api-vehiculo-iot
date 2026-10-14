import os
import pymysql
from pymysql.cursors import DictCursor
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()


class DatabaseConfig:
    def __init__(self):
        self.host = os.getenv("DB_HOST") or os.getenv("db_host", "localhost")
        self.port = int(os.getenv("DB_PORT") or os.getenv("db_port", "3306"))
        self.user = os.getenv("DB_USER") or os.getenv("db_user", "admin")
        self.password = os.getenv("DB_PASSWORD") or os.getenv("db_password", "")
        self.database = os.getenv("DB_NAME") or os.getenv("db_name", "vehiculo_iot")
        self.api_key = os.getenv("API_KEY") or os.getenv("api_key", "Admin1234#")


class DatabaseConnection:
    def __init__(self, config: DatabaseConfig):
        self._config = config

    def obtener_conexion(self):
        return pymysql.connect(
            host=self._config.host,
            port=self._config.port,
            user=self._config.user,
            password=self._config.password,
            database=self._config.database,
            cursorclass=DictCursor,
            autocommit=False
        )

    @contextmanager
    def transaccion(self):
        conexion = self.obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                yield cursor
            conexion.commit()
        except Exception:
            conexion.rollback()
            raise
        finally:
            conexion.close()

    @contextmanager
    def consulta(self):
        conexion = self.obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                yield cursor
        finally:
            conexion.close()