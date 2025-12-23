# 📱 Guía de Integración: CRM Standalone con Sistema de Facturación

## 🎯 Opciones de Integración

Existen 3 formas de integrar el CRM Standalone con un sistema de facturación:

## OPCIÓN 1️⃣: CRM Independiente (Recomendado para empezar)

### Descripción
El CRM funciona de forma **completamente independiente** en su propio servidor/proceso. Tu sistema de facturación lo consume a través de API REST.

### Ventajas ✅
- ✅ Fácil de mantener
- ✅ No afecta a tu sistema actual
- ✅ Escalable independientemente
- ✅ Puedes reemplazar/actualizar sin downtime
- ✅ Funciona en máquinas diferentes

### Desventajas ❌
- ❌ Requiere 2 servidores
- ❌ Sincronización manual de datos

### Implementación
```python
# En tu sistema de facturación
import requests

CRM_API = "http://crm-server:8000/api/crm"

# Crear cliente en CRM
def crear_cliente_factura(nombre, email, cif):
    response = requests.post(
        f"{CRM_API}/clientes",
        json={
            "nombre_completo": nombre,
            "email": email,
            "cif_nif": cif,
            "tipo_cliente": "empresa",
            "estado": "activo"
        }
    )
    cliente_crm = response.json()
    return cliente_crm["id"]

# Obtener cliente desde CRM
def obtener_cliente_crm(cliente_id):
    response = requests.get(f"{CRM_API}/clientes/{cliente_id}")
    return response.json()

# Registrar actividad cuando se crea factura
def registrar_factura_en_crm(cliente_id, monto_factura):
    requests.post(
        f"{CRM_API}/clientes/{cliente_id}/actividades",
        json={
            "tipo": "venta",
            "titulo": f"Factura por €{monto_factura}",
            "fecha": datetime.now().isoformat(),
            "completada": True
        }
    )
```

---

## OPCIÓN 2️⃣: CRM Integrado (Fusión en un Servidor)

### Descripción
Combinas el CRM Standalone con tu sistema de facturación en **un único servidor FastAPI**.

### Ventajas ✅
- ✅ Un solo servidor
- ✅ Fácil de desplegar
- ✅ Acceso directo a datos (sin HTTP)
- ✅ Transacciones ACID en una BD

### Desventajas ❌
- ❌ Más complejo de mantener
- ❌ Si uno cae, todo cae
- ❌ Difícil de escalar

### Implementación

```python
# Estructura integrada
Mi-Facturacion/
├── main.py                    # App principal
├── src/
│   ├── models/
│   │   ├── factura_models.py
│   │   ├── crm_models.py      ← Del CRM
│   │   └── producto_models.py
│   ├── repositories/
│   │   ├── factura_repo.py
│   │   ├── crm_repo.py        ← Del CRM
│   │   └── producto_repo.py
│   └── interface/
│       ├── factura_api.py
│       ├── crm_api.py         ← Del CRM
│       └── producto_api.py
└── database.db

# main.py
from fastapi import FastAPI
from src.interface import factura_api, crm_api

app = FastAPI()

# Incluir ambos routers
app.include_router(factura_api.router)
app.include_router(crm_api.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Pasos de Integración

1. **Copiar archivos CRM** a tu proyecto:
```bash
cp -r SyntexIA-CRM-Standalone/src/* tu-proyecto/src/
```

2. **Actualizar database.db** para usar una sola base de datos:
```python
# En ambos repositories
DB_PATH = "database.db"  # Mismo archivo para todo
```

3. **Combinar routers** en main.py:
```python
from src.interface.factura_api import router as factura_router
from src.interface.crm_api import router as crm_router

app.include_router(factura_router)
app.include_router(crm_router)
```

---

## OPCIÓN 3️⃣: Arquitectura de Microservicios (Escalada)

### Descripción
CRM y Facturación como **microservicios independientes** con comunicación asíncrona (Kafka, RabbitMQ).

### Ventajas ✅
- ✅ Ultra escalable
- ✅ Fácil de mantener separado
- ✅ Fallos aislados
- ✅ Deploy independiente

### Desventajas ❌
- ❌ Muy complejo
- ❌ Requiere Kafka/RabbitMQ
- ❌ Consistencia eventual

### Arquitectura
```
┌──────────────────────┐         ┌──────────────────────┐
│   CRM Service        │         │  Factura Service     │
│  (Puerto 8001)       │◄─────────►(Puerto 8002)        │
│                      │  Eventos │                      │
│  • Clientes          │  via     │  • Facturas          │
│  • Contactos         │ RabbitMQ │  • Reportes          │
│  • Actividades       │          │  • Pagos             │
└──────────────────────┘         └──────────────────────┘
         ▲                                 ▲
         │                                 │
         └─────────────────┬───────────────┘
                      Base de Datos
                    (PostgreSQL)
```

---

# 🚀 CÓMO IMPLEMENTARLO PASO A PASO

## Para tu amiga: Paso 1 - Clonar el Repositorio

```bash
# Ir a la carpeta donde quiere el CRM
cd ~/Proyectos

# Clonar el repositorio
git clone https://github.com/tu-usuario/SyntexIA-CRM-Standalone.git

# Entrar a la carpeta
cd SyntexIA-CRM-Standalone

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor
python main.py
```

## Para tu amiga: Paso 2 - Conectar con Sistema de Facturación (Opción 1)

### Archivo: `conectar_con_crm.py`

```python
"""
Módulo para conectar tu sistema de facturación con CRM Standalone
"""

import requests
from typing import Optional, Dict, Any
from datetime import datetime
import json

class ClienteCRM:
    """Cliente HTTP para comunicarse con CRM Standalone"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.crm_api = f"{base_url}/api/crm"
        self.timeout = 5
    
    # ========== CLIENTES ==========
    def crear_cliente(self, nombre: str, email: str, cif: str) -> Dict[str, Any]:
        """Crear cliente en CRM desde tu sistema de facturación"""
        response = requests.post(
            f"{self.crm_api}/clientes",
            json={
                "nombre_completo": nombre,
                "email": email,
                "cif_nif": cif,
                "tipo_cliente": "empresa",
                "estado": "activo"
            },
            timeout=self.timeout
        )
        return response.json()
    
    def obtener_cliente(self, cliente_id: str) -> Dict[str, Any]:
        """Obtener datos del cliente desde CRM"""
        response = requests.get(
            f"{self.crm_api}/clientes/{cliente_id}",
            timeout=self.timeout
        )
        return response.json()
    
    def listar_clientes(self, skip: int = 0, limit: int = 50) -> Dict[str, Any]:
        """Listar clientes de CRM"""
        response = requests.get(
            f"{self.crm_api}/clientes",
            params={"skip": skip, "limit": limit},
            timeout=self.timeout
        )
        return response.json()
    
    # ========== ACTIVIDADES ==========
    def registrar_factura_en_crm(
        self,
        cliente_id: str,
        numero_factura: str,
        monto: float,
        descripcion: str = None
    ):
        """Registrar factura como actividad en CRM"""
        requests.post(
            f"{self.crm_api}/clientes/{cliente_id}/actividades",
            json={
                "tipo": "venta",
                "titulo": f"Factura #{numero_factura}",
                "descripcion": descripcion or f"Factura por €{monto}",
                "fecha": datetime.now().isoformat(),
                "completada": True
            },
            timeout=self.timeout
        )
    
    def registrar_pago_en_crm(
        self,
        cliente_id: str,
        numero_factura: str,
        monto: float
    ):
        """Registrar pago como actividad en CRM"""
        requests.post(
            f"{self.crm_api}/clientes/{cliente_id}/actividades",
            json={
                "tipo": "pago",
                "titulo": f"Pago recibido - Factura #{numero_factura}",
                "descripcion": f"Pago de €{monto}",
                "fecha": datetime.now().isoformat(),
                "completada": True
            },
            timeout=self.timeout
        )
    
    # ========== OPORTUNIDADES ==========
    def crear_oportunidad(
        self,
        cliente_id: str,
        titulo: str,
        valor: float,
        probabilidad: float = 50
    ) -> Dict[str, Any]:
        """Crear oportunidad de venta en CRM"""
        response = requests.post(
            f"{self.crm_api}/clientes/{cliente_id}/oportunidades",
            json={
                "titulo": titulo,
                "descripcion": f"Oportunidad por €{valor}",
                "estado": "inicial",
                "valor_estimado": valor,
                "probabilidad_cierre": probabilidad
            },
            timeout=self.timeout
        )
        return response.json()
    
    # ========== ESTADÍSTICAS ==========
    def obtener_resumen_crm(self) -> Dict[str, Any]:
        """Obtener resumen ejecutivo del CRM"""
        response = requests.get(
            f"{self.crm_api}/resumen",
            timeout=self.timeout
        )
        return response.json()


# ========== EJEMPLOS DE USO ==========

if __name__ == "__main__":
    crm = ClienteCRM()  # Conecta a http://localhost:8000
    
    # 1. Crear cliente
    print("1️⃣  Crear cliente...")
    cliente = crm.crear_cliente(
        nombre="Acme Corporation",
        email="contact@acme.com",
        cif="ES12345678A"
    )
    cliente_id = cliente["id"]
    print(f"   Cliente creado: {cliente_id}")
    
    # 2. Registrar factura como actividad
    print("2️⃣  Registrar factura...")
    crm.registrar_factura_en_crm(
        cliente_id=cliente_id,
        numero_factura="FAC-2025-001",
        monto=500.00,
        descripcion="Factura de servicios de consultoría"
    )
    print("   ✅ Factura registrada en CRM")
    
    # 3. Crear oportunidad
    print("3️⃣  Crear oportunidad...")
    opp = crm.crear_oportunidad(
        cliente_id=cliente_id,
        titulo="Contrato anual de mantenimiento",
        valor=5000.00,
        probabilidad=75
    )
    print(f"   Oportunidad creada: {opp['id']}")
    
    # 4. Obtener resumen
    print("4️⃣  Obtener resumen CRM...")
    resumen = crm.obtener_resumen_crm()
    print(f"   Total clientes: {resumen['total_clientes']}")
    print(f"   Clientes activos: {resumen['clientes_activos']}")
    print(f"   Actividades pendientes: {resumen['actividades_pendientes']}")
```

## Para tu amiga: Paso 3 - Integrar en su Facturación

### Ejemplo: Crear factura e integrar con CRM

```python
# En tu_facturacion/crear_factura.py

from conectar_con_crm import ClienteCRM
from datetime import datetime

crm = ClienteCRM()

def crear_factura_completa(cliente_nombre, email, cif, items, total):
    """
    1. Crear cliente en BD de facturación
    2. Crear cliente en CRM
    3. Registrar factura en CRM
    4. Devolver información completa
    """
    
    # Paso 1: Verificar si cliente existe en CRM
    clientes_crm = crm.listar_clientes()
    cliente_crm = None
    
    for c in clientes_crm["clientes"]:
        if c["email"] == email:
            cliente_crm = c
            break
    
    # Paso 2: Si no existe, crear en CRM
    if not cliente_crm:
        print(f"Creando nuevo cliente en CRM: {cliente_nombre}")
        cliente_crm = crm.crear_cliente(cliente_nombre, email, cif)
    
    cliente_crm_id = cliente_crm["id"]
    
    # Paso 3: Crear factura en tu BD
    numero_factura = generar_numero_factura()
    factura = {
        "numero": numero_factura,
        "cliente_crm_id": cliente_crm_id,  # ← Guardar referencia CRM
        "cliente_nombre": cliente_nombre,
        "fecha": datetime.now(),
        "items": items,
        "total": total,
        "estado": "emitida"
    }
    guardar_factura_en_bd(factura)
    
    # Paso 4: Registrar en CRM
    crm.registrar_factura_en_crm(
        cliente_id=cliente_crm_id,
        numero_factura=numero_factura,
        monto=total,
        descripcion=f"Factura de {len(items)} productos"
    )
    
    print(f"✅ Factura #{numero_factura} creada")
    print(f"   Cliente en CRM: {cliente_crm_id}")
    print(f"   Total: €{total}")
    
    return factura

# Usar
if __name__ == "__main__":
    factura = crear_factura_completa(
        cliente_nombre="Empresa XYZ",
        email="empresa@xyz.com",
        cif="ES98765432B",
        items=[
            {"descripcion": "Servicio A", "cantidad": 1, "precio": 300},
            {"descripcion": "Servicio B", "cantidad": 2, "precio": 100}
        ],
        total=500.00
    )
```

---

# 📤 CÓMO SUBIRLO A GITHUB

## Paso 1: Crear repositorio en GitHub

1. Ir a https://github.com/new
2. Nombre: `SyntexIA-CRM-Standalone`
3. Descripción: "Independent CRM system built with FastAPI and SQLite"
4. Hacer público (para que tu amiga pueda clonar)
5. Crear repositorio (sin README, usaremos el nuestro)

## Paso 2: Pushear el código

```bash
# En tu terminal local
cd C:\Users\Usuario\Downloads\SyntexIA-CRM-Standalone

# Agregar remote
git remote add origin https://github.com/tu-usuario/SyntexIA-CRM-Standalone.git

# Cambiar rama a main (si necesario)
git branch -M main

# Pushear
git push -u origin main
```

## Paso 3: Tu amiga clona el repo

```bash
git clone https://github.com/tu-usuario/SyntexIA-CRM-Standalone.git

cd SyntexIA-CRM-Standalone

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt

python main.py
```

---

# ✅ CHECKLIST DE IMPLEMENTACIÓN

Para tu amiga:

- [ ] Clonar repositorio
- [ ] Crear entorno virtual
- [ ] Instalar dependencias (`pip install -r requirements.txt`)
- [ ] Ejecutar servidor (`python main.py`)
- [ ] Acceder a http://localhost:8000/docs
- [ ] Probar crear cliente en Swagger
- [ ] Copiar `conectar_con_crm.py` a su proyecto de facturación
- [ ] Actualizar URLs de API según su setup
- [ ] Integrar llamadas CRM en su código de facturación
- [ ] Hacer tests de integración
- [ ] Desplegar en producción

---

# 🆘 TROUBLESHOOTING PARA TU AMIGA

### Error: "ModuleNotFoundError: No module named 'fastapi'"
```bash
pip install -r requirements.txt
```

### Error: "Port 8000 already in use"
```bash
# Cambiar puerto en main.py
# O matar proceso
netstat -ano | findstr 8000
taskkill /PID <PID> /F
```

### Error: "Connection refused" desde su facturación
```python
# Verificar que CRM está corriendo
requests.get("http://localhost:8000/health")

# Si está en otra máquina, cambiar URL
crm = ClienteCRM("http://ip-del-servidor-crm:8000")
```

---

Espero que le sea útil a tu amiga. ¿Tienes preguntas sobre la integración? 🚀
