import lightgbm as lgb
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

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
