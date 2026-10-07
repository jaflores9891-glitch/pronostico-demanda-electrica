from datetime import date

import pandas as pd
import pytest

from pronostico_demanda_electrica.cleaning import (
    COLUMNAS_FINALES,
    leer_encabezado,
    normalizar_columnas,
    procesar_archivo,
)


def _crear_csv_con_encabezado(tmp_path, linea_encabezado, tabla=""):
    ruta = tmp_path / "mi_archivo.csv"
    ruta.write_text("relleno\n" * 7 + linea_encabezado + tabla)
    return ruta


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
    ruta = _crear_csv_con_encabezado(
        tmp_path, "LIQUIDACION 0 (Dia de Operacion: 11/09/2026)\n"
    )
    # Actuar
    encabezado = leer_encabezado(ruta)
    # Verificar
    assert encabezado == (0, date(2026, 9, 11))


def test_leer_encabezado_rechaza_formato_de_fecha_invalido(tmp_path):
    # Preparar
    ruta = _crear_csv_con_encabezado(
        tmp_path, "LIQUIDACION 0 (Dia de Operacion: 2026-09-11)\n"
    )
    # Actuar y verificar
    with pytest.raises(ValueError, match="Encabezado inesperado"):
        leer_encabezado(ruta)


def test_procesar_archivo_rechaza_liquidacion_invalida(tmp_path):
    # Preparar
    ruta = _crear_csv_con_encabezado(
        tmp_path, "LIQUIDACION 4 (Dia de Operacion: 11/09/2026)\n"
    )
    # Actuar y verificar
    with pytest.raises(ValueError, match="La liquidación es inválida"):
        procesar_archivo(ruta)


def test_procesar_archivo_devuelve_tabla_limpia(tmp_path):
    # Preparar
    encabezado = "LIQUIDACION 0 (Dia de Operacion: 11/09/2026)\n"

    tabla = (
        " Sistema, Area, Hora, Generacion (MWh), Importacion Total (MWh), Exportacion Total (MWh), Intercambio neto entre Gerencias (MWh), Estimacion de Demanda por Balance (MWh) \n"
        " BCA, BCA, 1, 100, 20, 10, ---, 110\n"
    )

    ruta = _crear_csv_con_encabezado(tmp_path, encabezado, tabla)

    # Actuar
    resultado = procesar_archivo(ruta)

    # Verificar
    assert list(resultado.columns) == COLUMNAS_FINALES
    assert resultado["fecha"].iloc[0] == date(2026, 9, 11)


def test_procesar_archivo_acepta_formato_alternativo(tmp_path):
    # Preparar
    encabezado = "LIQUIDACION 0 (Dia de Operacion: 11/09/2026)\n"
    tabla = (
        "CLV_SISTEMA,CLV_AREA,HORA,GENERACION,IMPORTACION,EXPORTACION,"
        "ENERGIA ENTRE GERENCIAS,BALANCE\n"
        "BCA,BCA,1,100,20,10,---,110\n"
    )
    ruta = _crear_csv_con_encabezado(tmp_path, encabezado, tabla)

    # Actuar
    resultado = procesar_archivo(ruta)

    # Verificar
    assert list(resultado.columns) == COLUMNAS_FINALES
    assert resultado["demanda_mwh"].iloc[0] == 110
