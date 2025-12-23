#!/usr/bin/env python3
# =====================================================
# 🚀 SyntexIA CRM Standalone — Aplicación Principal
# =====================================================
"""
Servidor FastAPI standalone para SyntexIA CRM.
Ejecutar con: python main.py
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.interface.crm_api import router as crm_router
from src.config.logger import get_logger

logger = get_logger("Main")

# =====================================================
# CONFIGURACIÓN FASTAPI
# =====================================================

app = FastAPI(
    title="SyntexIA CRM Standalone",
    description="📊 Sistema de Gestión de Relaciones con Clientes (CRM) - Independiente",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

# =====================================================
# MIDDLEWARE CORS
# =====================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# REGISTRO DE ROUTERS
# =====================================================

app.include_router(crm_router)

# =====================================================
# ENDPOINTS BÁSICOS
# =====================================================

@app.get("/", tags=["Health"])
def root():
    """Endpoint raíz - Verificar que el servidor está activo"""
    return {
        "status": "ok",
        "message": "✅ SyntexIA CRM Standalone está activo",
        "version": "1.0.0",
        "docs": "http://localhost:8000/docs"
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "SyntexIA CRM"}


@app.get("/api/version", tags=["Info"])
def get_version():
    """Obtener versión del servidor"""
    return {"version": "1.0.0", "name": "SyntexIA CRM Standalone"}


# =====================================================
# EVENT HANDLERS
# =====================================================

@app.on_event("startup")
async def startup_event():
    """Ejecutar al iniciar el servidor"""
    logger.info("🚀 SyntexIA CRM Standalone iniciado")
    logger.info("📍 Documentación disponible en: http://localhost:8000/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Ejecutar al detener el servidor"""
    logger.info("🛑 SyntexIA CRM Standalone detenido")


# =====================================================
# PUNTO DE ENTRADA
# =====================================================

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("🚀 Iniciando SyntexIA CRM Standalone")
    logger.info("=" * 60)
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info",
        access_log=True
    )
