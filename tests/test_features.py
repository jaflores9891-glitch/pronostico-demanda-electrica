import pandas as pd

from pronostico_demanda_electrica.features import agregar_variables


def test_lag_12_toma_el_mismo_mes_del_anio_anterior():
    # Preparar: 13 meses con 1, 2, ..., 13 GWh por día
    meses = pd.date_range("2022-01-01", periods=13, freq="MS")
    df = pd.DataFrame(
        {
            "region": "A",
            "mes": meses,
            "demanda_gwh": [(i + 1) * m.days_in_month for i, m in enumerate(meses)],
            "dias": meses.days_in_month,
        }
    )

    # Actuar
    resultado = agregar_variables(df)

    # Verificar: los primeros 12 no tienen lag; ene-2023 toma ene-2022 (1 GWh/día)
    assert resultado["lag_12"].isna().sum() == 12
    assert resultado["lag_12"].iloc[12] == 1.0
