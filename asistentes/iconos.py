import os
from typing import Optional

def iconos(carpeta: Optional[str], icono: str) -> str:
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if carpeta:
        return os.path.join(base, carpeta, icono)
    else:
        return os.path.join(base, icono)
