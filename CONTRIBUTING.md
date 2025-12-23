# 🤝 Guía de Contribución - SyntexIA CRM Standalone

## 👋 Bienvenido

¡Gracias por tu interés en contribuir a **SyntexIA CRM Standalone**!

Este documento proporciona pautas y procedimientos para contribuir al proyecto.

## 📋 Código de Conducta

- Sé respetuoso con otros contribuyentes
- Proporciona feedback constructivo
- Reporta bugs de manera clara y detallada
- Propone mejoras con ejemplos

## 🐛 Reportar Bugs

### Formato para reporte de bug
```
**Título:** [Descripción breve del problema]

**Descripción:**
Explicación detallada del bug

**Pasos para reproducir:**
1. Ir a...
2. Hacer clic en...
3. Notar que...

**Comportamiento esperado:**
Qué debería suceder

**Comportamiento actual:**
Qué sucede realmente

**Entorno:**
- OS: Windows 10 / macOS / Linux
- Python: 3.9 / 3.10 / 3.11
- Version: 1.0.0
```

## ✨ Solicitar Características

### Formato para feature request
```
**Título:** [Feature] Descripción clara y concisa

**Descripción:**
Por qué es importante esta característica

**Caso de uso:**
Cómo lo usaría un usuario final

**Alternativas consideradas:**
Otros enfoques que podrían funcionar

**Contexto adicional:**
Screenshots, ejemplos, referencias
```

## 🔄 Workflow de Desarrollo

### 1. Fork y Clone
```bash
git clone https://github.com/tu-usuario/SyntexIA-CRM-Standalone.git
cd SyntexIA-CRM-Standalone
```

### 2. Crear rama de feature
```bash
git checkout -b feature/nombre-feature
# o
git checkout -b fix/nombre-bug
```

### 3. Hacer cambios
```bash
# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Hacer cambios...
```

### 4. Probar cambios
```bash
# Tests unitarios
python -m pytest tests/ -v

# Test manual
python main.py
# Acceder a http://localhost:8000/docs
```

### 5. Commit y Push
```bash
git add .
git commit -m "feat: descripción clara de cambios"
git push origin feature/nombre-feature
```

### 6. Pull Request
- Crear PR con descripción detallada
- Referenciar issues relacionados (#123)
- Esperar revisión del equipo

## 📝 Estándares de Código

### Python Style Guide (PEP 8)
```python
# ✅ CORRECTO
def crear_cliente(cliente_data: ClienteCreate) -> Cliente:
    """Crear nuevo cliente en la base de datos."""
    cliente_id = f"cli_{uuid.uuid4().hex[:12]}"
    return Cliente(id=cliente_id, **cliente_data.dict())

# ❌ INCORRECTO
def crearCliente(clienteData):
    # Sin type hints
    # Sin docstring
    cliente_id = f"cli_{uuid.uuid4().hex[:12]}"
    return Cliente(id=cliente_id, **clienteData)
```

### Docstrings (Google Style)
```python
def registrar_pago(self, factura_id: str, monto: float) -> bool:
    """Registrar pago de una factura.
    
    Args:
        factura_id: ID único de la factura
        monto: Monto pagado en euros
        
    Returns:
        bool: True si el pago se registró exitosamente
        
    Raises:
        ValueError: Si la factura no existe
        
    Example:
        >>> resultado = repo.registrar_pago("fac_123", 100.50)
        >>> print(resultado)
        True
    """
```

### Type Hints
```python
# ✅ CORRECTO
def obtener_clientes(
    skip: int = 0,
    limit: int = 50
) -> List[Cliente]:
    """Obtener lista de clientes."""
    ...

# ❌ INCORRECTO
def obtener_clientes(skip, limit):
    """Obtener lista de clientes."""
    ...
```

### Validación con Pydantic v2
```python
# ✅ CORRECTO (Pydantic v2)
class Cliente(BaseModel):
    id: str
    nombre: str
    email: EmailStr  # Validación automática
    edad: Optional[int] = Field(None, ge=0, le=150)

# ❌ INCORRECTO (Pydantic v1 - no soportado)
class Cliente(BaseModel):
    id: str = Field(...)  # Ellipsis no permitido
```

## 🧪 Testing

### Estructura de Tests
```python
def test_crear_cliente():
    """Test crear cliente nuevo."""
    # Arrange
    payload = {"nombre": "Test Corp", "email": "test@example.com"}
    
    # Act
    response = requests.post(f"{CRM_API}/clientes", json=payload)
    
    # Assert
    assert response.status_code == 201
    assert response.json()["nombre"] == "Test Corp"
```

### Cobertura Mínima
- Nuevas features: 80%+ cobertura
- Bug fixes: Tests que reproducen el bug
- Refactoring: Mantener cobertura existente

## 📚 Documentación

### Documentar cambios en:
1. **README.md** - Si afecta uso del CRM
2. **ARCHITECTURE.md** - Si cambia arquitectura
3. **Docstrings** - En funciones/clases
4. **Comentarios inline** - Para lógica compleja

### Ejemplo de documentación
```python
def listar_clientes(
    skip: int = 0,
    limit: int = 50,
    estado: Optional[str] = None
) -> Tuple[List[Cliente], int]:
    """Listar clientes con paginación y filtros.
    
    Implementa paginación eficiente y búsqueda full-text
    en nombre, email y razón social.
    
    Args:
        skip: Número de registros a saltar (paginación)
        limit: Máximo número de registros (máximo 100)
        estado: Filtrar por estado (prospecto, activo, etc)
        
    Returns:
        Tupla de (lista_clientes, total_registros)
        
    Raises:
        ValueError: Si limit > 100
        
    Examples:
        >>> clientes, total = repo.listar_clientes(skip=0, limit=10)
        >>> print(f"Total: {total}, Mostrando: {len(clientes)}")
        Total: 150, Mostrando: 10
    """
```

## 🔐 Seguridad

### Checklist de Seguridad
- [ ] No hardcodear credenciales
- [ ] Usar parameterized queries (contra SQL injection)
- [ ] Validar todos los inputs (Pydantic)
- [ ] No loguear datos sensibles (contraseñas, tokens)
- [ ] Usar HTTPS en producción
- [ ] Implementar rate limiting si es necesario

## 📦 Release Process

### Versionado Semántico
```
MAJOR.MINOR.PATCH
v1.0.0

Cambios:
- MAJOR: cambios incompatibles (breaking changes)
- MINOR: nuevas features compatibles (features)
- PATCH: bug fixes (fixes)
```

### Ejemplo de cambios
```
v1.0.0 → v1.1.0 (nueva feature)
v1.1.0 → v1.1.1 (bug fix)
v1.1.1 → v2.0.0 (breaking change)
```

## 🚀 Performance

### Checklist de Performance
- [ ] Usar índices en BD para búsquedas frecuentes
- [ ] Implementar paginación en listados
- [ ] Cachear resultados cuando sea apropiado
- [ ] Usar connection pooling
- [ ] Evitar N+1 queries

## 📞 Soporte y Preguntas

- **Issues:** Para bugs y features
- **Discussions:** Para preguntas (próximamente)
- **Email:** info@syntexia.io
- **Docs:** Consultar README.md y ARCHITECTURE.md

## ✅ Checklist antes de PR

- [ ] Tests pasando (`pytest tests/ -v`)
- [ ] Código sigue PEP 8 (`black` u `pylint`)
- [ ] Type hints en todas las funciones
- [ ] Docstrings en funciones públicas
- [ ] README actualizado si es necesario
- [ ] Commit message claro y descriptivo
- [ ] Sin cambios no relacionados en el PR
- [ ] PR con descripción detallada

## 🎓 Recursos

- [PEP 8 - Python Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [Pydantic v2 Documentation](https://docs.pydantic.dev/)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Git Workflow](https://guides.github.com/introduction/flow/)

---

**¡Gracias por contribuir a SyntexIA CRM Standalone! 🙏**

Esperamos tus PRs, sugerencias y reportes de bugs.

Juntos hacemos el CRM mejor. 💪
