# API IoT - Sistema de Gestión y Monitoreo de Vehículos (Amazon RDS & FastAPI)

Repositorio oficial del proyecto de desarrollo de una API backend en Python utilizando **FastAPI**, **Programación Orientada a Objetos (POO)** y **Amazon RDS (MySQL)**, implementando 21 Procedimientos Almacenados y comunicación en tiempo real mediante **WebSockets**.

---

##  Características Principales
- **Arquitectura Modular (POO):** Separación estricta de responsabilidades en capas (`database`, `schemas`, `repositories`, `services`, `websocket_manager`).
- **Integración con Amazon RDS:** Conexión segura mediante variables de entorno y soporte para transacciones atómicas.
- **Cobertura de 21 Stored Procedures:** Operaciones CRUD completas y transaccionales para Vehículos, Comandos, Estado, Historial, DEMOs y Movimientos de DEMO.
- **Comunicación en Tiempo Real (WebSocket):** Transmisión de eventos de comandos individuales y secuencias de DEMO concurrentes sin afectar el historial en base de datos.
- **Documentación Interactiva:** Integración nativa con **Swagger UI** (`/docs`).

---

##  Tecnologías Utilizadas
- **Python 3.10+**
- **FastAPI** 
- **PyMySQL** 
- **Pydantic** 
- **Uvicorn** 
- **Git & GitHub** 

---

##  Instrucciones de Ejecución Local

### 1. Clonar el Repositorio
```bash
git clone [https://github.com/andres0524E/api-vehiculo-iot.git](https://github.com/andres0524E/api-vehiculo-iot.git)
cd api-vehiculo-iot