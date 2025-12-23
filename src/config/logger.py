import logging
from logging.handlers import RotatingFileHandler
import os

# 📁 Asegura que exista el directorio de logs
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
log_dir = os.path.join(base_dir, "logs")
os.makedirs(log_dir, exist_ok=True)

# 📄 Archivo principal de log
log_file = os.path.join(log_dir, "crm.log")

# ⚙️ Configuración de logging rotativo
logger = logging.getLogger("SyntexIA-CRM")
logger.setLevel(logging.INFO)

handler = RotatingFileHandler(log_file, maxBytes=2_000_000, backupCount=5)
formatter = logging.Formatter(
    "%(asctime)s — [%(levelname)s] — %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(handler)

def get_logger(name="SyntexIA-CRM"):
    return logger.getChild(name)
