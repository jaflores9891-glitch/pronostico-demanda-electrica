import pandas as pd
from sqlalchemy import Engine

SQL_DEMANDA_MENSUAL = """
SELECT
    date_trunc('month', fecha)::date AS mes,
    sistema,
    area,
    SUM(demanda_mwh) / 1000 AS demanda_gwh
FROM demanda_horaria
GROUP BY mes, sistema, area
ORDER BY sistema, area, mes
"""


def leer_demanda_mensual(engine: Engine) -> pd.DataFrame:
    """Devuelve la demanda mensual (GWh) de cada región, con los días de cada mes."""
    df = pd.read_sql(SQL_DEMANDA_MENSUAL, engine)
    df["mes"] = pd.to_datetime(df["mes"])
    df["region"] = df["sistema"] + "-" + df["area"]
    df["dias"] = df["mes"].dt.days_in_month
    return df
