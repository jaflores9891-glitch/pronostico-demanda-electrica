import zipfile
from pathlib import Path

from pronostico_demanda_electrica.cleaning import LIQUIDACION_ESPERADA

PATRON_LIQUIDACION = f"Balance_{LIQUIDACION_ESPERADA}_"


def extraer_liquidacion_0(ruta_zip: Path, destino: Path) -> int:
    """Extrae del .zip solo los CSV de la liquidación esperada. Devuelve cuántos extrajo."""
    destino.mkdir(parents=True, exist_ok=True)
    extraidos = 0
    with zipfile.ZipFile(ruta_zip) as z:
        for nombre in z.namelist():
            if PATRON_LIQUIDACION in nombre:
                z.extract(nombre, destino)
                extraidos += 1
    return extraidos
