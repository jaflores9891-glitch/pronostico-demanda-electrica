import lightgbm as lgb
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from pronostico_demanda_electrica.features import agregar_variables

FORMULA_OLS = "log_crecimiento ~ C(region)"
VARIABLES_LGBM = ["region", "mes_del_anio", "tendencia", "lag_12"]
PARAMETROS_LGBM = {
    "n_estimators": 200,
    "learning_rate": 0.05,
    "num_leaves": 7,
    "min_child_samples": 10,
    "random_state": 42,
    "verbose": -1,
}


def a_demanda(prueba: pd.DataFrame, log_crecimiento: pd.Series) -> pd.Series:
    """Convierte el crecimiento logarítmico pronosticado en demanda mensual (GWh)."""
    return prueba["lag_12"] * np.exp(log_crecimiento) * prueba["dias"]


def pronosticar_ols(entrenamiento: pd.DataFrame, prueba: pd.DataFrame) -> pd.Series:
    """OLS: crecimiento anual promedio de cada región."""
    modelo = smf.ols(FORMULA_OLS, data=entrenamiento).fit()
    return a_demanda(prueba, modelo.predict(prueba))


def _matriz(df: pd.DataFrame, regiones: list[str]) -> pd.DataFrame:
    """Prepara las variables de LightGBM con la región como categoría."""
    x = df[VARIABLES_LGBM].copy()
    x["region"] = pd.Categorical(x["region"], categories=regiones)
    return x


def pronosticar_lgbm(entrenamiento: pd.DataFrame, prueba: pd.DataFrame) -> pd.Series:
    """LightGBM: crecimiento anual según región, mes, tendencia y nivel del año anterior."""
    regiones = sorted(entrenamiento["region"].unique())
    modelo = lgb.LGBMRegressor(**PARAMETROS_LGBM)
    modelo.fit(_matriz(entrenamiento, regiones), entrenamiento["log_crecimiento"])
    prediccion = modelo.predict(_matriz(prueba, regiones))
    return a_demanda(prueba, pd.Series(prediccion, index=prueba.index))


HORIZONTE = 12


def pronosticar_futuro(mensual: pd.DataFrame, meses: int = HORIZONTE) -> pd.DataFrame:
    """Pronostica los próximos meses de cada región con el OLS entrenado con toda la historia."""
    datos = agregar_variables(mensual)
    ultimo_mes = datos["mes"].max()
    futuro = pd.DataFrame(
        [
            (region, ultimo_mes + pd.DateOffset(months=i))
            for region in sorted(datos["region"].unique())
            for i in range(1, meses + 1)
        ],
        columns=["region", "mes"],
    )
    futuro["mes"] = futuro["mes"].astype(datos["mes"].dtype)
    futuro["dias"] = futuro["mes"].dt.days_in_month
    anio_anterior = datos[["region", "mes", "gwh_dia"]].assign(
        mes=datos["mes"] + pd.DateOffset(years=1)
    )
    futuro = futuro.merge(anio_anterior, on=["region", "mes"], how="left")
    futuro = futuro.rename(columns={"gwh_dia": "lag_12"})
    entrenamiento = datos.dropna(subset=["log_crecimiento"])
    futuro["pronostico_gwh"] = pronosticar_ols(entrenamiento, futuro)
    return futuro[["region", "mes", "pronostico_gwh"]]


def crecimiento_esperado(mensual: pd.DataFrame, futuro: pd.DataFrame) -> pd.Series:
    """Crecimiento (%) de los próximos 12 meses frente a los últimos 12 meses reales."""
    corte = mensual["mes"].max() - pd.DateOffset(months=12)
    base = mensual[mensual["mes"] > corte].groupby("region")["demanda_gwh"].sum()
    pronostico = futuro.groupby("region")["pronostico_gwh"].sum()
    return ((pronostico / base - 1) * 100).sort_values(ascending=False)
