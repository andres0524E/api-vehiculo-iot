from app.database import DatabaseConnection


class StoredProcedureRepository:
    def __init__(self, db: DatabaseConnection):
        self._db = db

    def _limpiar_resultados(self, cursor):
        while cursor.nextset():
            pass

    def crear_vehiculo(self, nombre: str, modelo: str, descripcion: str, microcontrolador: str):
        with self._db.transaccion() as cursor:
            cursor.execute(
                "call sp_crear_vehiculo(%s, %s, %s, %s)",
                (nombre, modelo, descripcion, microcontrolador)
            )
            resultado = cursor.fetchone()
            self._limpiar_resultados(cursor)
            return resultado

    def obtener_vehiculos(self):
        with self._db.consulta() as cursor:
            cursor.execute("call sp_obtener_vehiculos()")
            resultados = cursor.fetchall()
            self._limpiar_resultados(cursor)
            return resultados

    def obtener_vehiculo(self, id_vehiculo: int):
        with self._db.consulta() as cursor:
            cursor.execute("call sp_obtener_vehiculo(%s)", (id_vehiculo,))
            resultado = cursor.fetchone()
            self._limpiar_resultados(cursor)
            return resultado

    def actualizar_vehiculo(self, id_vehiculo: int, nombre: str, modelo: str, descripcion: str, microcontrolador: str, activo: bool):
        with self._db.transaccion() as cursor:
            cursor.execute(
                "call sp_actualizar_vehiculo(%s, %s, %s, %s, %s, %s)",
                (id_vehiculo, nombre, modelo, descripcion, microcontrolador, int(activo))
            )
            self._limpiar_resultados(cursor)

    def eliminar_vehiculo(self, id_vehiculo: int):
        with self._db.transaccion() as cursor:
            cursor.execute("call sp_eliminar_vehiculo(%s)", (id_vehiculo,))
            self._limpiar_resultados(cursor)

    def crear_comando(self, id_vehiculo: int, nombre: str, codigo: int, descripcion: str):
        with self._db.transaccion() as cursor:
            cursor.execute(
                "call sp_crear_comando(%s, %s, %s, %s)",
                (id_vehiculo, nombre, codigo, descripcion)
            )
            resultado = cursor.fetchone()
            self._limpiar_resultados(cursor)
            return resultado

    def obtener_comandos_vehiculo(self, id_vehiculo: int):
        with self._db.consulta() as cursor:
            cursor.execute("call sp_obtener_comandos_vehiculo(%s)", (id_vehiculo,))
            resultados = cursor.fetchall()
            self._limpiar_resultados(cursor)
            return resultados

    def actualizar_comando(self, id_comando: int, nombre: str, codigo: int, descripcion: str, activo: bool):
        with self._db.transaccion() as cursor:
            cursor.execute(
                "call sp_actualizar_comando(%s, %s, %s, %s, %s)",
                (id_comando, nombre, codigo, descripcion, int(activo))
            )
            self._limpiar_resultados(cursor)

    def eliminar_comando(self, id_comando: int):
        with self._db.transaccion() as cursor:
            cursor.execute("call sp_eliminar_comando(%s)", (id_comando,))
            self._limpiar_resultados(cursor)

    def actualizar_estado(self, id_vehiculo: int, id_comando: int, conectado: bool):
        with self._db.transaccion() as cursor:
            cursor.execute(
                "call sp_actualizar_estado(%s, %s, %s)",
                (id_vehiculo, id_comando, int(conectado))
            )
            self._limpiar_resultados(cursor)

    def obtener_estado(self, id_vehiculo: int):
        with self._db.consulta() as cursor:
            cursor.execute("call sp_obtener_estado(%s)", (id_vehiculo,))
            resultado = cursor.fetchone()
            self._limpiar_resultados(cursor)
            return resultado

    def registrar_historial(self, id_vehiculo: int, id_comando: int, origen: str):
        with self._db.transaccion() as cursor:
            cursor.execute(
                "call sp_registrar_historial(%s, %s, %s)",
                (id_vehiculo, id_comando, origen)
            )
            resultado = cursor.fetchone()
            self._limpiar_resultados(cursor)
            return resultado

    def obtener_historial(self, id_vehiculo: int):
        with self._db.consulta() as cursor:
            cursor.execute("call sp_obtener_historial(%s)", (id_vehiculo,))
            resultados = cursor.fetchall()
            self._limpiar_resultados(cursor)
            return resultados

    def crear_demo(self, id_vehiculo: int, nombre: str, descripcion: str):
        with self._db.transaccion() as cursor:
            cursor.execute(
                "call sp_crear_demo(%s, %s, %s)",
                (id_vehiculo, nombre, descripcion)
            )
            resultado = cursor.fetchone()
            self._limpiar_resultados(cursor)
            return resultado

    def obtener_demos(self, id_vehiculo: int):
        with self._db.consulta() as cursor:
            cursor.execute("call sp_obtener_demos(%s)", (id_vehiculo,))
            resultados = cursor.fetchall()
            self._limpiar_resultados(cursor)
            return resultados

    def actualizar_demo(self, id_demo: int, nombre: str, descripcion: str, activo: bool):
        with self._db.transaccion() as cursor:
            cursor.execute(
                "call sp_actualizar_demo(%s, %s, %s, %s)",
                (id_demo, nombre, descripcion, int(activo))
            )
            self._limpiar_resultados(cursor)

    def eliminar_demo(self, id_demo: int):
        with self._db.transaccion() as cursor:
            cursor.execute("call sp_eliminar_demo(%s)", (id_demo,))
            self._limpiar_resultados(cursor)

    def agregar_movimiento_demo(self, id_demo: int, id_comando: int, orden: int, duracion_ms: int, pausa_ms: int):
        with self._db.transaccion() as cursor:
            cursor.execute(
                "call sp_agregar_movimiento_demo(%s, %s, %s, %s, %s)",
                (id_demo, id_comando, orden, duracion_ms, pausa_ms)
            )
            resultado = cursor.fetchone()
            self._limpiar_resultados(cursor)
            return resultado

    def obtener_movimientos_demo(self, id_demo: int):
        with self._db.consulta() as cursor:
            cursor.execute("call sp_obtener_movimientos_demo(%s)", (id_demo,))
            resultados = cursor.fetchall()
            self._limpiar_resultados(cursor)
            return resultados

    def actualizar_movimiento_demo(self, id_movimiento_demo: int, id_comando: int, orden: int, duracion_ms: int, pausa_ms: int):
        with self._db.transaccion() as cursor:
            cursor.execute(
                "call sp_actualizar_movimiento_demo(%s, %s, %s, %s, %s)",
                (id_movimiento_demo, id_comando, orden, duracion_ms, pausa_ms)
            )
            self._limpiar_resultados(cursor)

    def eliminar_movimiento_demo(self, id_movimiento_demo: int):
        with self._db.transaccion() as cursor:
            cursor.execute("call sp_eliminar_movimiento_demo(%s)", (id_movimiento_demo,))
            self._limpiar_resultados(cursor)

    def registrar_movimiento_individual_atomico(self, id_vehiculo: int, id_comando: int, conectado: bool, origen: str):
        with self._db.transaccion() as cursor:
            cursor.execute(
                "call sp_actualizar_estado(%s, %s, %s)",
                (id_vehiculo, id_comando, int(conectado))
            )
            self._limpiar_resultados(cursor)
            cursor.execute(
                "call sp_registrar_historial(%s, %s, %s)",
                (id_vehiculo, id_comando, origen)
            )
            self._limpiar_resultados(cursor)