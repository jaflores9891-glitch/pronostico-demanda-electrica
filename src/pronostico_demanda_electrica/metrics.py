import pandas as pd


def mae(real: pd.Series, pronostico: pd.Series) -> float:
    """Error absoluto medio, en las mismas unidades que la demanda."""
    return float((real - pronostico).abs().mean())


def wape(real: pd.Series, pronostico: pd.Series) -> float:
    """Error absoluto total como porcentaje de la demanda real total."""
    return float((real - pronostico).abs().sum() / real.sum() * 100)


def evaluar_por_region(prueba: pd.DataFrame, pronostico: pd.Series) -> pd.DataFrame:
    """Calcula MAE y WAPE de cada región."""
    filas = []
    for region, datos in prueba.groupby("region"):
        p = pronostico.loc[datos.index]
        filas.append(
            {
                "region": region,
                "mae_gwh": mae(datos["demanda_gwh"], p),
                "wape_%": wape(datos["demanda_gwh"], p),
            }
        )
    return pd.DataFrame(filas).set_index("region")
