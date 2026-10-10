import pandas as pd


def mae(real: pd.Series, pronostico: pd.Series) -> float:
    """Error absoluto medio, en las mismas unidades que la demanda."""
    return float((real - pronostico).abs().mean())


def wape(real: pd.Series, pronostico: pd.Series) -> float:
    """Error absoluto total como porcentaje de la demanda real total."""
    return float((real - pronostico).abs().sum() / real.sum() * 100)
