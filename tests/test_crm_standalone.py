#!/usr/bin/env python3
# =====================================================
# 🧪 Tests para SyntexIA CRM Standalone
# =====================================================
"""
Suite de tests para validar funcionamiento del CRM.
Ejecutar con: python -m pytest tests/test_crm_standalone.py -v
"""

import pytest
import requests
import json
import time
from datetime import datetime

# =====================================================
# CONFIGURACIÓN DE TESTS
# =====================================================

BASE_URL = "http://127.0.0.1:8000"
CRM_API = f"{BASE_URL}/api/crm"
TIMEOUT = 5

# Variables globales para guardar IDs
cliente_id = None
actividad_id = None
oportunidad_id = None

# =====================================================
# FIXTURES
# =====================================================

@pytest.fixture(scope="session", autouse=True)
def esperar_servidor():
    """Esperar a que el servidor esté listo"""
    for intento in range(10):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print("\n✅ Servidor detectado y listo\n")
                return
        except requests.exceptions.ConnectionError:
            print(f"⏳ Esperando servidor... intento {intento + 1}/10")
            time.sleep(1)
    
    raise Exception("❌ El servidor no está disponible en http://127.0.0.1:8000")


# =====================================================
# TESTS BÁSICOS
# =====================================================

def test_servidor_activo():
    """Verificar que el servidor esté activo"""
    response = requests.get(f"{BASE_URL}/", timeout=TIMEOUT)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    print("✅ Servidor está activo")


def test_health_check():
    """Verificar health check"""
    response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("✅ Health check pasado")


def test_version():
    """Obtener versión del servidor"""
    response = requests.get(f"{BASE_URL}/api/version", timeout=TIMEOUT)
    assert response.status_code == 200
    assert "version" in response.json()
    print(f"✅ Versión: {response.json()['version']}")


# =====================================================
# TESTS CLIENTES
# =====================================================

def test_crear_cliente():
    """Test crear cliente"""
    global cliente_id
    
    payload = {
        "nombre_completo": "Test Client Corp",
        "email": f"test-{int(time.time())}@example.com",
        "cif_nif": f"ES{int(time.time())}",
        "tipo_cliente": "empresa",
        "estado": "prospecto",
        "segmento": "premium"
    }
    
    response = requests.post(
        f"{CRM_API}/clientes",
        json=payload,
        timeout=TIMEOUT
    )
    
    assert response.status_code == 201, f"Error: {response.text}"
    data = response.json()
    cliente_id = data["id"]
    
    assert data["nombre_completo"] == payload["nombre_completo"]
    assert data["email"] == payload["email"]
    print(f"✅ Cliente creado: {cliente_id}")


def test_obtener_cliente():
    """Test obtener cliente por ID"""
    if not cliente_id:
        pytest.skip("Cliente no creado")
    
    response = requests.get(
        f"{CRM_API}/clientes/{cliente_id}",
        timeout=TIMEOUT
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == cliente_id
    print(f"✅ Cliente obtenido: {cliente_id}")


def test_listar_clientes():
    """Test listar clientes"""
    response = requests.get(
        f"{CRM_API}/clientes?skip=0&limit=10",
        timeout=TIMEOUT
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "clientes" in data
    assert "total" in data
    assert isinstance(data["clientes"], list)
    print(f"✅ Clientes listados: {data['total']} total")


def test_actualizar_cliente():
    """Test actualizar cliente"""
    if not cliente_id:
        pytest.skip("Cliente no creado")
    
    payload = {
        "estado": "activo",
        "segmento": "enterprise"
    }
    
    response = requests.put(
        f"{CRM_API}/clientes/{cliente_id}",
        json=payload,
        timeout=TIMEOUT
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["estado"] == "activo"
    print(f"✅ Cliente actualizado")


# =====================================================
# TESTS CONTACTOS
# =====================================================

def test_agregar_contacto():
    """Test agregar contacto a cliente"""
    if not cliente_id:
        pytest.skip("Cliente no creado")
    
    payload = {
        "tipo": "email",
        "valor": f"contacto-{int(time.time())}@test.com",
        "principal": True,
        "verificado": False
    }
    
    response = requests.post(
        f"{CRM_API}/clientes/{cliente_id}/contactos",
        json=payload,
        timeout=TIMEOUT
    )
    
    assert response.status_code == 201
    print(f"✅ Contacto agregado")


def test_listar_contactos():
    """Test listar contactos"""
    if not cliente_id:
        pytest.skip("Cliente no creado")
    
    response = requests.get(
        f"{CRM_API}/clientes/{cliente_id}/contactos",
        timeout=TIMEOUT
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    print(f"✅ Contactos listados: {len(data)} contactos")


# =====================================================
# TESTS ACTIVIDADES
# =====================================================

def test_crear_actividad():
    """Test crear actividad"""
    global actividad_id
    
    if not cliente_id:
        pytest.skip("Cliente no creado")
    
    payload = {
        "tipo": "llamada",
        "titulo": "Llamada de seguimiento",
        "descripcion": "Seguimiento de propuesta",
        "fecha": datetime.now().isoformat(),
        "completada": False,
        "responsable": "Juan Pérez"
    }
    
    response = requests.post(
        f"{CRM_API}/clientes/{cliente_id}/actividades",
        json=payload,
        timeout=TIMEOUT
    )
    
    assert response.status_code == 201
    data = response.json()
    actividad_id = data.get("id")
    assert data["titulo"] == payload["titulo"]
    print(f"✅ Actividad creada: {actividad_id}")


def test_listar_actividades():
    """Test listar actividades"""
    if not cliente_id:
        pytest.skip("Cliente no creado")
    
    response = requests.get(
        f"{CRM_API}/clientes/{cliente_id}/actividades",
        timeout=TIMEOUT
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    print(f"✅ Actividades listadas: {len(data)} actividades")


# =====================================================
# TESTS OPORTUNIDADES
# =====================================================

def test_crear_oportunidad():
    """Test crear oportunidad"""
    global oportunidad_id
    
    if not cliente_id:
        pytest.skip("Cliente no creado")
    
    payload = {
        "titulo": "Venta grande potencial",
        "descripcion": "Posible contrato anual",
        "estado": "inicial",
        "valor_estimado": 50000,
        "probabilidad_cierre": 30
    }
    
    response = requests.post(
        f"{CRM_API}/clientes/{cliente_id}/oportunidades",
        json=payload,
        timeout=TIMEOUT
    )
    
    assert response.status_code == 201
    data = response.json()
    oportunidad_id = data.get("id")
    assert data["titulo"] == payload["titulo"]
    print(f"✅ Oportunidad creada: {oportunidad_id}")


def test_listar_oportunidades():
    """Test listar oportunidades"""
    if not cliente_id:
        pytest.skip("Cliente no creado")
    
    response = requests.get(
        f"{CRM_API}/clientes/{cliente_id}/oportunidades",
        timeout=TIMEOUT
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    print(f"✅ Oportunidades listadas: {len(data)} oportunidades")


# =====================================================
# TESTS ESTADÍSTICAS
# =====================================================

def test_obtener_resumen():
    """Test obtener resumen ejecutivo del CRM"""
    response = requests.get(
        f"{CRM_API}/resumen",
        timeout=TIMEOUT
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verificar campos principales
    assert "total_clientes" in data
    assert "clientes_activos" in data
    assert "actividades_pendientes" in data
    assert "oportunidades_proximas_cerrar" in data
    
    print(f"✅ Resumen CRM obtenido")
    print(f"   📊 Total clientes: {data['total_clientes']}")
    print(f"   👥 Clientes activos: {data['clientes_activos']}")
    print(f"   📋 Actividades pendientes: {data['actividades_pendientes']}")
    print(f"   💼 Oportunidades próximas: {data['oportunidades_proximas_cerrar']}")


# =====================================================
# TESTS ERRORES
# =====================================================

def test_cliente_no_encontrado():
    """Test error cuando cliente no existe"""
    response = requests.get(
        f"{CRM_API}/clientes/cliente_inexistente_12345",
        timeout=TIMEOUT
    )
    
    assert response.status_code == 404
    print("✅ Error 404 correcto para cliente inexistente")


def test_actividad_en_cliente_no_encontrado():
    """Test error crear actividad en cliente inexistente"""
    payload = {
        "tipo": "email",
        "titulo": "Test",
        "fecha": datetime.now().isoformat()
    }
    
    response = requests.post(
        f"{CRM_API}/clientes/inexistente/actividades",
        json=payload,
        timeout=TIMEOUT
    )
    
    assert response.status_code == 404
    print("✅ Error 404 correcto para cliente inexistente en actividad")


# =====================================================
# CLEANUP
# =====================================================

def test_eliminar_cliente():
    """Test eliminar cliente (cleanup)"""
    global cliente_id
    
    if not cliente_id:
        pytest.skip("Cliente no creado")
    
    response = requests.delete(
        f"{CRM_API}/clientes/{cliente_id}",
        timeout=TIMEOUT
    )
    
    assert response.status_code == 204
    print(f"✅ Cliente eliminado: {cliente_id}")
    cliente_id = None


# =====================================================
# PUNTO DE ENTRADA
# =====================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🧪 SyntexIA CRM Standalone - Suite de Tests")
    print("=" * 60)
    print("\nEjecutar con:")
    print("  python -m pytest tests/test_crm_standalone.py -v\n")
    print("O ejecutar este archivo directamente:")
    print("  python tests/test_crm_standalone.py\n")
