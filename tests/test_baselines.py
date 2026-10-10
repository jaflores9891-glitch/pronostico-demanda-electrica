import pandas as pd

from pronostico_demanda_electrica.baselines import (
    dividir_entrenamiento_prueba,
    naive_estacional,
)


def test_naive_estacional_usa_demanda_diaria_del_anio_anterior():
    # Preparar: feb-2024 (29 días, 1 GWh/día) y feb-2025 (28 días)
    df = pd.DataFrame(
        {
            "region": ["A", "A"],
            "mes": pd.to_datetime(["2024-02-01", "2025-02-01"]),
            "demanda_gwh": [29.0, 30.0],
            "dias": [29, 28],
        }
    )
    entrenamiento, prueba = dividir_entrenamiento_prueba(df, pd.Timestamp("2025-01-01"))

    # Actuar
    pronostico = naive_estacional(entrenamiento, prueba)

    # Verificar: 1 GWh/día × 28 días
    assert pronostico.tolist() == [28.0]
