import numpy as np
import pandas as pd

ANIO_INICIAL = 2022


def agregar_variables(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega las variables del modelo y el objetivo (crecimiento logarítmico anual)."""
    df = df.sort_values(["region", "mes"]).copy()
    df["gwh_dia"] = df["demanda_gwh"] / df["dias"]
    df["lag_12"] = df.groupby("region")["gwh_dia"].shift(12)
    df["mes_del_anio"] = df["mes"].dt.month
    df["tendencia"] = (df["mes"].dt.year - ANIO_INICIAL) * 12 + df["mes"].dt.month - 1
    df["log_crecimiento"] = np.log(df["gwh_dia"] / df["lag_12"])
    return df
