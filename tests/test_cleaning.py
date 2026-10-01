from datetime import date

import pandas as pd
import pytest

from pronostico_demanda_electrica.cleaning import (
    leer_encabezado,
    normalizar_columnas,
)


def test_normalizar_columnas_renombra_sin_modificar_el_original():
    # Preparar: nombres como vienen de CENACE, con espacios
    df = pd.DataFrame(
        columns=[" Area", " Hora", " Estimacion de Demanda por Balance (MWh) "]
    )

    # Actuar
    resultado = normalizar_columnas(df)

    # Verificar normalizacion y cambio de nombres de columnas
    assert list(resultado.columns) == ["area", "hora", "demanda_mwh"], (
        "Fallo la normalizacion"
    )
    # Verificar que no se modifico el df original
    assert list(df.columns) == [
        " Area",
        " Hora",
        " Estimacion de Demanda por Balance (MWh) ",
    ], "Se modifico el df original"


def test_leer_encabezado_devuelve_liquidacion_y_fecha(tmp_path):
    # Preparar
    ruta = tmp_path / "mi_archivo.csv"

    ruta.write_text(
        "linea1\n"
        "linea2\n"
        "linea3\n"
        "linea4\n"
        "linea5\n"
        "linea6\n"
        "linea7\n"
        "LIQUIDACION 0 (Dia de Operacion: 11/09/2026)"
    )
    # Actuar
    encabezado = leer_encabezado(ruta)
    # Verificar
    assert encabezado == (0, date(2026, 9, 11))


def test_leer_encabezado_rechaza_formato_de_fecha_invalido(tmp_path):
    # Preparar
    ruta = tmp_path / "mi_archivo.csv"
    ruta.write_text(
        "línea 1\n"
        "línea 2\n"
        "línea 3\n"
        "línea 4\n"
        "línea 5\n"
        "línea 6\n"
        "línea 7\n"
        "LIQUIDACION 0 (Dia de Operacion: 2026-09-11)\n"
    )
    # Actuar y verificar
    with pytest.raises(ValueError, match="Encabezado inesperado"):
        leer_encabezado(ruta)
