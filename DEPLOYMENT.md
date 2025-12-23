# 🚀 Guía de Despliegue - SyntexIA CRM Standalone

## Índice
1. [Despliegue Local](#despliegue-local)
2. [Despliegue en Producción](#despliegue-en-producción)
3. [Despliegue con Docker](#despliegue-con-docker)
4. [Nginx como Reverse Proxy](#nginx-como-reverse-proxy)
5. [HTTPS con Let's Encrypt](#https-con-lets-encrypt)
6. [Monitoreo y Mantenimiento](#monitoreo-y-mantenimiento)

---

## Despliegue Local

### Requisitos Mínimos
- Python 3.9+
- pip
- 50MB de espacio en disco

### Instalación
```bash
# 1. Navegar al directorio
cd SyntexIA-CRM-Standalone

# 2. Crear entorno virtual
python -m venv .venv

# 3. Activar entorno virtual
# En Windows:
.venv\Scripts\activate
# En macOS/Linux:
source .venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Ejecutar
python main.py
```

### Verificación
```bash
# En otra terminal
curl http://localhost:8000/health
# Respuesta esperada: {"status": "healthy", "service": "SyntexIA CRM"}
```

---

## Despliegue en Producción

### Requisitos Mínimos
- Servidor Linux (Ubuntu 20.04+ recomendado)
- Python 3.9+
- Git
- Supervisor o systemd
- Nginx

### 1. Preparación del Servidor

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python
sudo apt install python3.9 python3.9-venv python3.9-dev -y

# Instalar otras dependencias
sudo apt install git nginx supervisor curl -y

# Crear usuario para la aplicación
sudo useradd -m -s /bin/bash crm-app
```

### 2. Clonar Repositorio

```bash
# Cambiar a usuario de aplicación
su - crm-app

# Clonar
git clone <repo-url> SyntexIA-CRM-Standalone
cd SyntexIA-CRM-Standalone

# Crear y activar entorno virtual
python3.9 -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configurar Supervisor

Crear archivo `/etc/supervisor/conf.d/crm-app.conf`:

```ini
[program:crm-app]
command=/home/crm-app/SyntexIA-CRM-Standalone/.venv/bin/python main.py
directory=/home/crm-app/SyntexIA-CRM-Standalone
user=crm-app
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/crm-app/SyntexIA-CRM-Standalone/logs/supervisor.log
environment=PATH="/home/crm-app/SyntexIA-CRM-Standalone/.venv/bin"
```

Activar:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start crm-app
```

Verificar:
```bash
sudo supervisorctl status crm-app
```

---

## Despliegue con Docker

### Dockerfile

Crear `Dockerfile` en raíz del proyecto:

```dockerfile
FROM python:3.9-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de requisitos
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

# Crear directorio de logs
RUN mkdir -p logs

# Puerto expuesto
EXPOSE 8000

# Comando para iniciar
CMD ["python", "main.py"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  crm:
    build: .
    container_name: syntexia-crm
    ports:
      - "8000:8000"
    volumes:
      - ./crm.db:/app/crm.db
      - ./logs:/app/logs
    environment:
      - SERVER_HOST=0.0.0.0
      - SERVER_PORT=8000
    restart: always
    networks:
      - crm-network

networks:
  crm-network:
    driver: bridge
```

### Ejecutar con Docker

```bash
# Compilar imagen
docker build -t syntexia-crm:1.0.0 .

# Ejecutar contenedor
docker run -d \
  --name syntexia-crm \
  -p 8000:8000 \
  -v $(pwd)/crm.db:/app/crm.db \
  -v $(pwd)/logs:/app/logs \
  syntexia-crm:1.0.0

# Verificar
docker ps
curl http://localhost:8000/health
```

Alternativa con docker-compose:

```bash
docker-compose up -d
docker-compose logs -f crm
```

---

## Nginx como Reverse Proxy

### Configuración Nginx

Crear `/etc/nginx/sites-available/crm.example.com`:

```nginx
upstream crm_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    listen [::]:80;
    server_name crm.example.com;

    # Redirigir a HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name crm.example.com;

    # Certificados SSL (ver sección HTTPS)
    ssl_certificate /etc/letsencrypt/live/crm.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/crm.example.com/privkey.pem;

    # Seguridad SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Logs
    access_log /var/log/nginx/crm_access.log;
    error_log /var/log/nginx/crm_error.log;

    # Proxy
    location / {
        proxy_pass http://crm_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # WebSocket (si es necesario)
    location /ws {
        proxy_pass http://crm_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    # Gzip compression
    gzip on;
    gzip_types text/plain application/json text/css;
    gzip_min_length 1000;
}
```

### Activar sitio

```bash
# Crear enlace simbólico
sudo ln -s /etc/nginx/sites-available/crm.example.com /etc/nginx/sites-enabled/

# Probar configuración
sudo nginx -t

# Recargar Nginx
sudo systemctl reload nginx
```

---

## HTTPS con Let's Encrypt

### Instalar Certbot

```bash
sudo apt install certbot python3-certbot-nginx -y
```

### Obtener Certificado

```bash
sudo certbot certonly --nginx -d crm.example.com

# O con auto-renovación:
sudo certbot --nginx -d crm.example.com
```

### Auto-renovación

```bash
# Verificar que está configurado
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# Probar renovación manual
sudo certbot renew --dry-run
```

---

## Monitoreo y Mantenimiento

### 1. Health Check

```bash
# Script de verificación (health-check.sh)
#!/bin/bash

RESPONSE=$(curl -s http://localhost:8000/health)
if echo "$RESPONSE" | grep -q "healthy"; then
    echo "✅ CRM está activo"
    exit 0
else
    echo "❌ CRM está inactivo"
    exit 1
fi
```

Ejecutar periódicamente con cron:
```bash
# Cada 5 minutos
*/5 * * * * /home/crm-app/health-check.sh >> /home/crm-app/health-check.log 2>&1
```

### 2. Logs

```bash
# Ver logs en tiempo real
tail -f logs/crm.log

# Ver últimas 100 líneas
tail -n 100 logs/crm.log

# Buscar errores
grep ERROR logs/crm.log
```

### 3. Backup

```bash
# Script de backup (backup.sh)
#!/bin/bash

BACKUP_DIR="/backups/crm"
DATE=$(date +%Y-%m-%d_%H-%M-%S)

mkdir -p $BACKUP_DIR

# Backup de base de datos
cp crm.db $BACKUP_DIR/crm_$DATE.db

# Backup de logs
tar czf $BACKUP_DIR/logs_$DATE.tar.gz logs/

echo "✅ Backup completado: $DATE"
```

Ejecutar diariamente:
```bash
0 2 * * * /home/crm-app/backup.sh
```

### 4. Actualizar

```bash
cd /home/crm-app/SyntexIA-CRM-Standalone

# Obtener cambios
git pull origin main

# Actualizar dependencias
source .venv/bin/activate
pip install -r requirements.txt --upgrade

# Reiniciar aplicación
sudo supervisorctl restart crm-app
```

---

## Checklist de Despliegue

### Pre-Despliegue
- [ ] Código testeado localmente
- [ ] Tests pasando (pytest)
- [ ] Documentación actualizada
- [ ] Variables de entorno configuradas
- [ ] Base de datos respaldada

### Despliegue
- [ ] Clonar repositorio
- [ ] Crear entorno virtual
- [ ] Instalar dependencias
- [ ] Configurar supervisor o systemd
- [ ] Configurar Nginx
- [ ] Instalar certificado SSL
- [ ] Iniciar aplicación

### Post-Despliegue
- [ ] Verificar health check
- [ ] Probar endpoints principales
- [ ] Revisar logs
- [ ] Configurar monitoreo
- [ ] Configurar backups
- [ ] Notificar usuarios

---

## Troubleshooting

### Aplicación no inicia
```bash
# Ver logs de supervisor
sudo tail -f /var/log/supervisor/crm-app.log

# O logs directos
tail -f logs/crm.log
```

### Puerto ya está en uso
```bash
# Encontrar proceso
sudo lsof -i :8000

# Matar proceso
sudo kill -9 <PID>
```

### Problemas de permiso
```bash
# Verificar propietario
ls -la /home/crm-app/SyntexIA-CRM-Standalone

# Cambiar propietario
sudo chown -R crm-app:crm-app /home/crm-app/SyntexIA-CRM-Standalone
```

### Base de datos bloqueada
```bash
# Eliminar archivo de bloqueo (SQLite)
rm crm.db-journal

# Recrear base de datos
rm crm.db
python main.py
```

---

## Performance Tuning

### Configuración de Uvicorn
En `main.py`, ajustar:

```python
uvicorn.run(
    app,
    host="127.0.0.1",
    port=8000,
    workers=4,              # Aumentar según CPU
    loop="uvloop",          # Más rápido que asyncio
    log_level="info",       # Reducir logging en prod
    access_log=False        # Desactivar logs HTTP si no se necesitan
)
```

### Límites del Sistema
```bash
# Aumentar límite de archivos abiertos
ulimit -n 65535

# Hacer persistente en /etc/security/limits.conf
crm-app soft nofile 65535
crm-app hard nofile 65535
```

---

## Escalabilidad Futura

### Multiple Workers
```bash
# Con Gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

### Load Balancing
```nginx
upstream crm_backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}
```

### Migración a PostgreSQL
```python
# En lugar de SQLite
SQLALCHEMY_DATABASE_URL = "postgresql://user:pwd@host/crm"
```

---

**Última actualización:** $(date)
**Versión:** 1.0.0
