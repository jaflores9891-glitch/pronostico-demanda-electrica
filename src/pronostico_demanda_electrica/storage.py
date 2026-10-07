import os

import pandas as pd
from sqlalchemy import Engine, create_engine, text

TABLA = "demanda_horaria"

SQL_CREAR_TABLA = """
CREATE TABLE IF NOT EXISTS demanda_horaria (
    fecha DATE NOT NULL,
    hora SMALLINT NOT NULL,
    sistema TEXT NOT NULL,
    area TEXT NOT NULL,
    demanda_mwh DOUBLE PRECISION NOT NULL,
    PRIMARY KEY (fecha, hora, sistema, area)
)
"""

SQL_VACIAR_TABLA = "TRUNCATE demanda_horaria"


def crear_engine() -> Engine:
    """Crea la conexión a PostgreSQL usando la variable de entorno DATABASE_URL."""
    return create_engine(os.environ["DATABASE_URL"])


def crear_tabla(engine: Engine) -> None:
    """Crea la tabla de demanda horaria si todavía no existe."""
    with engine.begin() as conexion:
        conexion.execute(text(SQL_CREAR_TABLA))


def recargar_demanda(engine: Engine, df: pd.DataFrame) -> int:
    """Reemplaza todo el contenido de la tabla por el DataFrame. Devuelve las filas cargadas."""
    with engine.begin() as conexion:
        conexion.execute(text(SQL_VACIAR_TABLA))
        df.to_sql(TABLA, conexion, if_exists="append", index=False, chunksize=10_000)
    return len(df)
