"""
Sincroniza MEMORY.md desde la carpeta de Claude Code al repo del workspace.
Ejecutar al final de cada sesión antes de hacer commit y push.
"""
import shutil
from pathlib import Path

SRC = Path.home() / ".claude" / "projects" / "C--Users-Ferd-Castell-Claude" / "memory" / "MEMORY.md"
DST = Path(__file__).parent / "memory" / "MEMORY.md"

if SRC.exists():
    shutil.copy2(SRC, DST)
    print(f"Sincronizado: {SRC} -> {DST}")
else:
    print(f"Archivo origen no encontrado: {SRC}")
