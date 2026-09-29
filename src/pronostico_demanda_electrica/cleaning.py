import re
from datetime import date, datetime
from pathlib import Path

import pandas as pd

LINEAS_ENCABEZADO = 8

COLUMNAS = {
    "Sistema": "sistema",
    "Area": "area",
    "Hora": "hora",
    "Generacion (MWh)": "generacion_mwh",
    "Importacion Total (MWh)": "importacion_mwh",
    "Exportacion Total (MWh)": "exportacion_mwh",
    "Intercambio neto entre Gerencias (MWh)": "intercambio_mwh",
    "Estimacion de Demanda por Balance (MWh)": "demanda_mwh",
}


def leer_csv_cenace(ruta: Path) -> pd.DataFrame:
    """Lee un CSV de CENACE saltando el encabezado descriptivo."""
    df = pd.read_csv(ruta, skiprows=LINEAS_ENCABEZADO)
    return df


def normalizar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    """Quita espacios de los nombres y los renombra al vocabulario del proyecto."""
    return df.rename(columns=str.strip).rename(columns=COLUMNAS)


COLUMNAS_FINALES = ["fecha", "sistema", "area", "hora", "demanda_mwh"]


def seleccionar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    """Conserva solo las columnas que usa el proyecto."""
    return df[COLUMNAS_FINALES]


LINEA_LIQUIDACION = 7
PATRON_ENCABEZADO = r"LIQUIDACION (\d+) \(Dia de Operacion: (\d{2}/\d{2}/\d{4})\)"
FORMATO_FECHA = "%d/%m/%Y"


def leer_encabezado(ruta: Path) -> tuple[int, date]:
    "Devuelve la liquidacion y el dia de operacion de un CSV de CENACE."
    with open(ruta) as f:
        linea = f.readlines()[LINEA_LIQUIDACION]

    coincidencia = re.search(PATRON_ENCABEZADO, linea)
    if coincidencia is None:
        raise ValueError(f"Encabezado inesperado en {ruta}: {linea!r}")
    liquidacion = int(coincidencia.group(1))
    texto_fecha = coincidencia.group(2)
    # CENACE reporta un día de calendario: no se usa hora ni zona horaria.
    fecha = datetime.strptime(texto_fecha, FORMATO_FECHA).date()  # noqa: DTZ007
    return liquidacion, fecha


LIQUIDACION_ESPERADA = 0


def procesar_archivo(ruta: Path) -> pd.DataFrame:
    """Convierte un CSV crudo de CENACE en la tabla limpia del proyecto."""
    liquidacion, fecha = leer_encabezado(ruta)
    if liquidacion != LIQUIDACION_ESPERADA:
        raise ValueError(f"La liquidación es inválida en {ruta}: {liquidacion}")
    df = leer_csv_cenace(ruta)
    df = normalizar_columnas(df)
    df = df.assign(fecha=fecha)
    return seleccionar_columnas(df)
