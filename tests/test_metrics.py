import pandas as pd
import pytest

from pronostico_demanda_electrica.metrics import mae, wape


def test_mae_promedia_errores_absolutos():
    real = pd.Series([100.0, 200.0])
    pronostico = pd.Series([110.0, 180.0])
    assert mae(real, pronostico) == 15.0


def test_wape_divide_error_total_entre_demanda_total():
    real = pd.Series([100.0, 200.0])
    pronostico = pd.Series([110.0, 180.0])
    assert wape(real, pronostico) == pytest.approx(10.0)
