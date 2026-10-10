import pandas as pd

INICIO_PRUEBA = pd.Timestamp("2025-09-01")


def dividir_entrenamiento_prueba(
    df: pd.DataFrame, inicio_prueba: pd.Timestamp = INICIO_PRUEBA
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Separa los datos por fecha: todo lo anterior a inicio_prueba es entrenamiento."""
    entrenamiento = df[df["mes"] < inicio_prueba]
    prueba = df[df["mes"] >= inicio_prueba]
    return entrenamiento, prueba


def naive_estacional(entrenamiento: pd.DataFrame, prueba: pd.DataFrame) -> pd.Series:
    """Repite la demanda diaria del mismo mes del año anterior, por los días del mes."""
    anio_anterior = entrenamiento.assign(
        gwh_dia=entrenamiento["demanda_gwh"] / entrenamiento["dias"],
        mes=entrenamiento["mes"] + pd.DateOffset(years=1),
    )[["region", "mes", "gwh_dia"]]
    unido = prueba.merge(anio_anterior, on=["region", "mes"], how="left")
    return pd.Series((unido["gwh_dia"] * unido["dias"]).to_numpy(), index=prueba.index)


def promedio_ultimos_12(entrenamiento: pd.DataFrame, prueba: pd.DataFrame) -> pd.Series:
    """Usa la demanda diaria promedio de los últimos 12 meses, por los días del mes."""
    corte = entrenamiento["mes"].max() - pd.DateOffset(months=12)
    ultimos = entrenamiento[entrenamiento["mes"] > corte]
    por_region = ultimos.groupby("region")[["demanda_gwh", "dias"]].sum()
    gwh_dia = por_region["demanda_gwh"] / por_region["dias"]
    return prueba["region"].map(gwh_dia) * prueba["dias"]
