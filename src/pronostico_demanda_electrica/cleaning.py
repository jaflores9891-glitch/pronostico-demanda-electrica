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
