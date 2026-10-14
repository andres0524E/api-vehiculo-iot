from typing import Optional
from pydantic import BaseModel, Field


class VehiculoCrearSchema(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=80)
    modelo: str = Field(..., min_length=1, max_length=80)
    descripcion: Optional[str] = Field(default="", max_length=255)
    microcontrolador: str = Field(..., min_length=1, max_length=50)


class VehiculoActualizarSchema(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=80)
    modelo: str = Field(..., min_length=1, max_length=80)
    descripcion: Optional[str] = Field(default="", max_length=255)
    microcontrolador: str = Field(..., min_length=1, max_length=50)
    activo: bool = Field(default=True)


class ComandoCrearSchema(BaseModel):
    id_vehiculo: int = Field(..., gt=0)
    nombre: str = Field(..., min_length=1, max_length=60)
    codigo: int = Field(..., ge=0)
    descripcion: Optional[str] = Field(default="", max_length=255)


class ComandoActualizarSchema(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=60)
    codigo: int = Field(..., ge=0)
    descripcion: Optional[str] = Field(default="", max_length=255)
    activo: bool = Field(default=True)


class EstadoActualizarSchema(BaseModel):
    id_vehiculo: int = Field(..., gt=0)
    id_comando: int = Field(..., gt=0)
    conectado: bool = Field(default=False)


class HistorialRegistrarSchema(BaseModel):
    id_vehiculo: int = Field(..., gt=0)
    id_comando: int = Field(..., gt=0)
    origen: str = Field(default="API-FASTAPI", min_length=1, max_length=50)


class MovimientoIndividualSchema(BaseModel):
    id_vehiculo: int = Field(..., gt=0)
    id_comando: int = Field(..., gt=0)
    origen: str = Field(default="THUNDER-CLIENT", min_length=1, max_length=50)


class DemoCrearSchema(BaseModel):
    id_vehiculo: int = Field(..., gt=0)
    nombre: str = Field(..., min_length=1, max_length=80)
    descripcion: Optional[str] = Field(default="", max_length=255)


class DemoActualizarSchema(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=80)
    descripcion: Optional[str] = Field(default="", max_length=255)
    activo: bool = Field(default=True)


class MovimientoDemoCrearSchema(BaseModel):
    id_demo: int = Field(..., gt=0)
    id_comando: int = Field(..., gt=0)
    orden: int = Field(..., gt=0)
    duracion_ms: int = Field(..., gt=0, le=60000)
    pausa_ms: int = Field(..., ge=0, le=60000)


class MovimientoDemoActualizarSchema(BaseModel):
    id_comando: int = Field(..., gt=0)
    orden: int = Field(..., gt=0)
    duracion_ms: int = Field(..., gt=0, le=60000)
    pausa_ms: int = Field(..., ge=0, le=60000)


class DemoEjecutarSchema(BaseModel):
    id_vehiculo: int = Field(..., gt=0)
    id_demo: int = Field(..., gt=0)