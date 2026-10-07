from pathlib import Path

import pandas as pd
from sqlalchemy import text

from pronostico_demanda_electrica.cleaning import procesar_archivo
from pronostico_demanda_electrica.ingestion import extraer_liquidacion_0
from pronostico_demanda_electrica.storage import (
    crear_engine,
    crear_tabla,
    recargar_demanda,
)

CARPETA_ZIP = Path("data/raw/cenace/zip")
CARPETA_CSV = Path("data/raw/cenace/csv")


def main() -> None:
    """Extrae, limpia y carga en PostgreSQL toda la demanda de CENACE."""
    # 1. Ingesta: extraer los CSV de liquidación 0 de cada .zip
    for ruta_zip in sorted(CARPETA_ZIP.glob("*.zip")):
        n = extraer_liquidacion_0(ruta_zip, CARPETA_CSV)
        print(f"{ruta_zip.name}: {n} archivos extraídos")

    # 2. Limpieza: procesar cada CSV y separar los que fallen
    tablas, omitidos = [], []
    for ruta in sorted(CARPETA_CSV.glob("*.csv")):
        try:
            tablas.append(procesar_archivo(ruta))
        except ValueError as error:
            omitidos.append((ruta.name, error))
    df = pd.concat(tablas, ignore_index=True)

    # 3. Almacenamiento: recargar la tabla completa
    engine = crear_engine()
    crear_tabla(engine)
    cargadas = recargar_demanda(engine, df)
    with engine.connect() as conexion:
        en_base = conexion.execute(
            text("SELECT COUNT(*) FROM demanda_horaria")
        ).scalar()

    # 4. Resumen
    print(f"Procesados: {len(tablas)} | Omitidos: {len(omitidos)}")
    for nombre, error in omitidos:
        print(f"  OMITIDO {nombre}: {error}")
    print(f"Filas cargadas: {cargadas} | Filas en la base: {en_base}")


if __name__ == "__main__":
    main()
