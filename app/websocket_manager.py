from datetime import datetime, timezone
from fastapi import WebSocket


class WebSocketManager:
    def __init__(self):
        self._conexiones: dict[int, list[WebSocket]] = {}

    async def conectar(self, id_vehiculo: int, websocket: WebSocket):
        await websocket.accept()
        if id_vehiculo not in self._conexiones:
            self._conexiones[id_vehiculo] = []
        self._conexiones[id_vehiculo].append(websocket)

    def desconectar(self, id_vehiculo: int, websocket: WebSocket):
        if id_vehiculo in self._conexiones:
            if websocket in self._conexiones[id_vehiculo]:
                self._conexiones[id_vehiculo].remove(websocket)
            if not self._conexiones[id_vehiculo]:
                del self._conexiones[id_vehiculo]

    def tiene_clientes(self, id_vehiculo: int) -> bool:
        return bool(self._conexiones.get(id_vehiculo))

    async def enviar_personal(self, websocket: WebSocket, evento: str, id_vehiculo: int, datos: dict):
        mensaje = {
            "evento": evento,
            "id_vehiculo": id_vehiculo,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **datos
        }
        await websocket.send_json(mensaje)

    async def transmitir_a_vehiculo(self, id_vehiculo: int, evento: str, datos: dict):
        if id_vehiculo not in self._conexiones:
            return
        mensaje = {
            "evento": evento,
            "id_vehiculo": id_vehiculo,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **datos
        }
        clientes_inactivos = []
        for ws in list(self._conexiones[id_vehiculo]):
            try:
                await ws.send_json(mensaje)
            except Exception:
                clientes_inactivos.append(ws)
        for ws in clientes_inactivos:
            self.desconectar(id_vehiculo, ws)