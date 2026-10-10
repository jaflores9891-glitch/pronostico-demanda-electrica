import pandas as pd
import pytest

from pronostico_demanda_electrica.models import pronosticar_futuro


def test_pronosticar_futuro_da_12_meses_sin_huecos():
    # Preparar: 2 años con 1 GWh/día constante (crecimiento cero)
    meses = pd.date_range("2024-01-01", "2025-12-01", freq="MS")
    mensual = pd.DataFrame(
        {
            "region": "A",
            "mes": meses,
            "demanda_gwh": meses.days_in_month * 1.0,
            "dias": meses.days_in_month,
        }
    )

    # Actuar
    futuro = pronosticar_futuro(mensual)

    # Verificar: 12 meses desde ene-2026 y, sin crecimiento, 1 GWh/día × días
    assert len(futuro) == 12
    assert futuro["mes"].min() == pd.Timestamp("2026-01-01")
    assert futuro["pronostico_gwh"].tolist() == pytest.approx(
        futuro["mes"].dt.days_in_month.tolist()
    )
