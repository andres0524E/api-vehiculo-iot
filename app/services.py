import asyncio
from fastapi import HTTPException
from app.repositories import StoredProcedureRepository
from app.websocket_manager import WebSocketManager


class VehiculoIoTService:
    def __init__(self, repo: StoredProcedureRepository, ws_manager: WebSocketManager):
        self._repo = repo
        self._ws = ws_manager
        self._demos_activas: dict[int, asyncio.Task] = {}
        self._eventos_cancelacion: dict[int, asyncio.Event] = {}

    def _serializar(self, datos):
        if isinstance(datos, list):
            return [self._serializar(item) for item in datos]
        if isinstance(datos, dict):
            nuevo = {}
            for k, v in datos.items():
                if hasattr(v, "isoformat"):
                    nuevo[k] = v.isoformat()
                else:
                    nuevo[k] = v
            return nuevo
        return datos

    # --- vehiculos ---
    def crear_vehiculo(self, datos):
        res = self._repo.crear_vehiculo(datos.nombre, datos.modelo, datos.descripcion or "", datos.microcontrolador)
        return self._serializar(res)

    def obtener_vehiculos(self):
        return self._serializar(self._repo.obtener_vehiculos())

    def obtener_vehiculo(self, id_vehiculo: int):
        vehiculo = self._repo.obtener_vehiculo(id_vehiculo)
        if not vehiculo:
            raise HTTPException(status_code=404, detail="vehiculo no encontrado")
        return self._serializar(vehiculo)

    def actualizar_vehiculo(self, id_vehiculo: int, datos):
        self.obtener_vehiculo(id_vehiculo)
        self._repo.actualizar_vehiculo(
            id_vehiculo, datos.nombre, datos.modelo, datos.descripcion or "", datos.microcontrolador, datos.activo
        )
        return {"mensaje": "vehiculo actualizado correctamente", "id_vehiculo": id_vehiculo}

    def eliminar_vehiculo(self, id_vehiculo: int):
        self.obtener_vehiculo(id_vehiculo)
        self._repo.eliminar_vehiculo(id_vehiculo)
        return {"mensaje": "vehiculo eliminado correctamente", "id_vehiculo": id_vehiculo}

    # --- comandos ---
    def crear_comando(self, datos):
        self.obtener_vehiculo(datos.id_vehiculo)
        res = self._repo.crear_comando(datos.id_vehiculo, datos.nombre, datos.codigo, datos.descripcion or "")
        return self._serializar(res)

    def obtener_comandos_vehiculo(self, id_vehiculo: int):
        self.obtener_vehiculo(id_vehiculo)
        return self._serializar(self._repo.obtener_comandos_vehiculo(id_vehiculo))

    def actualizar_comando(self, id_comando: int, datos):
        self._repo.actualizar_comando(id_comando, datos.nombre, datos.codigo, datos.descripcion or "", datos.activo)
        return {"mensaje": "comando actualizado correctamente", "id_comando": id_comando}

    def eliminar_comando(self, id_comando: int):
        self._repo.eliminar_comando(id_comando)
        return {"mensaje": "comando eliminado correctamente", "id_comando": id_comando}

    # --- estado e historial directo ---
    def obtener_estado(self, id_vehiculo: int):
        self.obtener_vehiculo(id_vehiculo)
        estado = self._repo.obtener_estado(id_vehiculo)
        return self._serializar(estado) if estado else {"id_vehiculo": id_vehiculo, "estado": "sin estado registrado"}

    def actualizar_estado(self, datos):
        self.obtener_vehiculo(datos.id_vehiculo)
        self._repo.actualizar_estado(datos.id_vehiculo, datos.id_comando, datos.conectado)
        return {"mensaje": "estado actualizado", "id_vehiculo": datos.id_vehiculo, "id_comando": datos.id_comando}

    def registrar_historial(self, datos):
        self.obtener_vehiculo(datos.id_vehiculo)
        res = self._repo.registrar_historial(datos.id_vehiculo, datos.id_comando, datos.origen)
        return self._serializar(res)

    def obtener_historial_ultimos_diez(self, id_vehiculo: int):
        self.obtener_vehiculo(id_vehiculo)
        historial = self._repo.obtener_historial(id_vehiculo) or []
        historial_ordenado = sorted(
            historial,
            key=lambda x: x.get("id_historial") or x.get("fecha_ejecucion") or 0,
            reverse=True
        )
        ultimos_diez = historial_ordenado[:10]
        return {
            "id_vehiculo": id_vehiculo,
            "total_devueltos": len(ultimos_diez),
            "limite_maximo": 10,
            "movimientos": self._serializar(ultimos_diez)
        }

    # --- movimiento individual (paso 5) ---
    async def ejecutar_movimiento_individual(self, datos):
        vehiculo = self._repo.obtener_vehiculo(datos.id_vehiculo)
        if not vehiculo:
            raise HTTPException(status_code=404, detail="el vehiculo no existe")
        if not bool(vehiculo.get("activo", 1)):
            raise HTTPException(status_code=400, detail="el vehiculo no esta activo")

        comandos = self._repo.obtener_comandos_vehiculo(datos.id_vehiculo) or []
        comando_valido = next((c for c in comandos if c.get("id_comando") == datos.id_comando), None)
        if not comando_valido:
            raise HTTPException(status_code=400, detail="el comando no existe o no pertenece a este vehiculo")
        if not bool(comando_valido.get("activo", 1)):
            raise HTTPException(status_code=400, detail="el comando se encuentra inactivo")

        conectado_actual = self._ws.tiene_clientes(datos.id_vehiculo)

        await asyncio.to_thread(
            self._repo.registrar_movimiento_individual_atomico,
            datos.id_vehiculo,
            datos.id_comando,
            conectado_actual,
            datos.origen
        )

        evento_ws = {
            "id_comando": comando_valido.get("id_comando"),
            "comando": comando_valido.get("nombre"),
            "codigo": comando_valido.get("codigo"),
            "origen": datos.origen,
            "conectado": conectado_actual
        }
        await self._ws.transmitir_a_vehiculo(datos.id_vehiculo, "movimiento_individual", evento_ws)

        return {
            "mensaje": "movimiento individual registrado exitosamente",
            "id_vehiculo": datos.id_vehiculo,
            **evento_ws
        }

    # --- demos y movimientos demo ---
    def crear_demo(self, datos):
        self.obtener_vehiculo(datos.id_vehiculo)
        res = self._repo.crear_demo(datos.id_vehiculo, datos.nombre, datos.descripcion or "")
        return self._serializar(res)

    def obtener_demos(self, id_vehiculo: int):
        self.obtener_vehiculo(id_vehiculo)
        return self._serializar(self._repo.obtener_demos(id_vehiculo))

    def actualizar_demo(self, id_demo: int, datos):
        self._repo.actualizar_demo(id_demo, datos.nombre, datos.descripcion or "", datos.activo)
        return {"mensaje": "demo actualizada correctamente", "id_demo": id_demo}

    def eliminar_demo(self, id_demo: int):
        self._repo.eliminar_demo(id_demo)
        return {"mensaje": "demo eliminada correctamente", "id_demo": id_demo}

    def agregar_movimiento_demo(self, datos):
        res = self._repo.agregar_movimiento_demo(
            datos.id_demo, datos.id_comando, datos.orden, datos.duracion_ms, datos.pausa_ms
        )
        return self._serializar(res)

    def obtener_movimientos_demo(self, id_demo: int):
        movimientos = self._repo.obtener_movimientos_demo(id_demo)
        return self._serializar(movimientos)

    def actualizar_movimiento_demo(self, id_movimiento_demo: int, datos):
        self._repo.actualizar_movimiento_demo(
            id_movimiento_demo, datos.id_comando, datos.orden, datos.duracion_ms, datos.pausa_ms
        )
        return {"mensaje": "movimiento de demo actualizado", "id_movimiento_demo": id_movimiento_demo}

    def eliminar_movimiento_demo(self, id_movimiento_demo: int):
        self._repo.eliminar_movimiento_demo(id_movimiento_demo)
        return {"mensaje": "movimiento de demo eliminado", "id_movimiento_demo": id_movimiento_demo}

    # --- ejecucion y cancelacion de demo por websocket (pasos 8 y 9) ---
    async def iniciar_demo(self, id_vehiculo: int, id_demo: int):
        if id_vehiculo in self._demos_activas and not self._demos_activas[id_vehiculo].done():
            raise HTTPException(status_code=409, detail="ya existe una demo en ejecucion para este vehiculo")

        vehiculo = self._repo.obtener_vehiculo(id_vehiculo)
        if not vehiculo or not bool(vehiculo.get("activo", 1)):
            raise HTTPException(status_code=404, detail="vehiculo inexistente o inactivo")

        demos = self._repo.obtener_demos(id_vehiculo) or []
        demo_actual = next((d for d in demos if d.get("id_demo") == id_demo), None)
        if not demo_actual:
            raise HTTPException(status_code=404, detail="la demo no existe o no pertenece al vehiculo indicado")
        if not bool(demo_actual.get("activo", 1)):
            raise HTTPException(status_code=400, detail="la demo solicitada esta inactiva")

        movimientos = self._repo.obtener_movimientos_demo(id_demo) or []
        if not movimientos:
            raise HTTPException(status_code=400, detail="la demo no tiene movimientos configurados")

        movimientos_ordenados = sorted(movimientos, key=lambda m: m.get("orden", 0))
        cancel_event = asyncio.Event()
        self._eventos_cancelacion[id_vehiculo] = cancel_event

        tarea = asyncio.create_task(
            self._procesar_secuencia_demo(id_vehiculo, id_demo, demo_actual.get("nombre", ""), movimientos_ordenados, cancel_event)
        )
        self._demos_activas[id_vehiculo] = tarea

        return {
            "mensaje": "ejecucion de demo iniciada por websocket sin registro en historial",
            "id_vehiculo": id_vehiculo,
            "id_demo": id_demo,
            "nombre_demo": demo_actual.get("nombre"),
            "total_movimientos": len(movimientos_ordenados)
        }

    async def _procesar_secuencia_demo(self, id_vehiculo: int, id_demo: int, nombre_demo: str, movimientos: list, cancel_event: asyncio.Event):
        try:
            await self._ws.transmitir_a_vehiculo(id_vehiculo, "demo_inicio", {
                "id_demo": id_demo,
                "nombre_demo": nombre_demo,
                "total_movimientos": len(movimientos)
            })

            for mov in movimientos:
                if cancel_event.is_set():
                    break

                id_cmd = mov.get("id_comando")
                nombre_cmd = mov.get("nombre_comando") or mov.get("comando") or mov.get("nombre")
                codigo_cmd = mov.get("codigo")
                orden = mov.get("orden")
                duracion_ms = int(mov.get("duracion_ms", 0))
                pausa_ms = int(mov.get("pausa_ms", 0))

                conectado = self._ws.tiene_clientes(id_vehiculo)
                await asyncio.to_thread(self._repo.actualizar_estado, id_vehiculo, id_cmd, conectado)

                await self._ws.transmitir_a_vehiculo(id_vehiculo, "demo_movimiento", {
                    "id_demo": id_demo,
                    "orden": orden,
                    "id_comando": id_cmd,
                    "comando": nombre_cmd,
                    "codigo": codigo_cmd,
                    "duracion_ms": duracion_ms,
                    "pausa_ms": pausa_ms
                })

                await asyncio.sleep(duracion_ms / 1000.0)
                if cancel_event.is_set():
                    break
                if pausa_ms > 0:
                    await asyncio.sleep(pausa_ms / 1000.0)

            if cancel_event.is_set():
                await self._ws.transmitir_a_vehiculo(id_vehiculo, "demo_cancelada", {
                    "id_demo": id_demo,
                    "accion_segura": "DETENER"
                })
            else:
                await self._ws.transmitir_a_vehiculo(id_vehiculo, "demo_fin", {
                    "id_demo": id_demo,
                    "nombre_demo": nombre_demo,
                    "estado": "completada"
                })
        except Exception as exc:
            await self._ws.transmitir_a_vehiculo(id_vehiculo, "demo_error", {
                "id_demo": id_demo,
                "detalle": "falla controlada durante la secuencia",
                "accion_segura": "DETENER"
            })
        finally:
            self._demos_activas.pop(id_vehiculo, None)
            self._eventos_cancelacion.pop(id_vehiculo, None)

    async def cancelar_demo(self, id_vehiculo: int):
        evento = self._eventos_cancelacion.get(id_vehiculo)
        tarea = self._demos_activas.get(id_vehiculo)
        if not evento or not tarea or tarea.done():
            raise HTTPException(status_code=404, detail="no hay ninguna demo activa para este vehiculo")
        evento.set()
        return {
            "mensaje": "solicitud de cancelacion enviada con prioridad de detencion segura",
            "id_vehiculo": id_vehiculo
        }