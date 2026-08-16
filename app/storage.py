"""
app/storage.py
Configuración del almacenamiento de archivos para FastAPI y SQLAdmin.
"""

import os
from fastapi_storages import FileSystemStorage

os.makedirs("app/img", exist_ok=True)
storage = FileSystemStorage(path="app/img")
