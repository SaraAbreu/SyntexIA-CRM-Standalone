#!/usr/bin/env python3
# =====================================================
# 🚀 Script de Iniciación Rápida
# =====================================================
"""
Script para iniciar rápidamente el CRM Standalone.
Ejecutar: python quick_start.py
"""

import subprocess
import sys
import os
import time
import platform

def print_header():
    """Mostrar encabezado"""
    print("\n" + "="*70)
    print("🚀 SyntexIA CRM Standalone - Quick Start")
    print("="*70 + "\n")

def check_python():
    """Verificar versión de Python"""
    version = sys.version_info
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("❌ Se requiere Python 3.9 o superior")
        return False
    return True

def check_venv():
    """Verificar si estamos en un entorno virtual"""
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    if in_venv:
        print(f"✅ Entorno virtual activo: {sys.prefix}")
    else:
        print("⚠️  No hay entorno virtual activo")
        print("   Se recomienda crear uno: python -m venv .venv")
    
    return True

def install_requirements():
    """Instalar dependencias"""
    print("\n📦 Verificando e instalando dependencias...")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("✅ Dependencias instaladas correctamente")
            return True
        else:
            print(f"❌ Error instalando dependencias:\n{result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Timeout al instalar dependencias")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_database():
    """Verificar base de datos"""
    if os.path.exists("crm.db"):
        print("✅ Base de datos existe: crm.db")
    else:
        print("📝 La base de datos se creará automáticamente al iniciar")

def start_server():
    """Iniciar el servidor"""
    print("\n" + "="*70)
    print("🚀 Iniciando servidor...")
    print("="*70 + "\n")
    
    print("📍 Accedible en:")
    print("   • API: http://127.0.0.1:8000")
    print("   • Documentación Swagger: http://127.0.0.1:8000/docs")
    print("   • Health Check: http://127.0.0.1:8000/health")
    print("\n💡 Presiona Ctrl+C para detener el servidor\n")
    
    try:
        subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("\n\n🛑 Servidor detenido")
        sys.exit(0)

def main():
    """Función principal"""
    print_header()
    
    # 1. Verificar Python
    print("📋 Verificando requisitos...")
    if not check_python():
        sys.exit(1)
    
    # 2. Verificar entorno virtual
    check_venv()
    
    # 3. Instalar dependencias
    if not install_requirements():
        sys.exit(1)
    
    # 4. Verificar base de datos
    print("\n🗄️  Verificando base de datos...")
    check_database()
    
    # 5. Iniciar servidor
    start_server()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Adiós!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
