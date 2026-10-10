# Notas de la Fase 7: App y despliegue

App pública: https://pronostico-demanda-electrica-mx.streamlit.app/

## Arquitectura
CENACE (.zip) → pipeline.py → PostgreSQL en Neon → app de Streamlit (Streamlit Community Cloud)

- El mismo código corre en local (Docker) y en la nube (Neon): solo cambia DATABASE_URL.
- Local: `uv run --env-file .env streamlit run app/app.py`
- Cargar Neon: `uv run --env-file .env.neon python -m pronostico_demanda_electrica.pipeline`

## Pronóstico a futuro (`models.py`)
- `pronosticar_futuro`: entrena el OLS con toda la historia y pronostica los 12 meses
  siguientes (sep-2026 a ago-2027). El lag_12 de cada mes futuro ya existe: no hay fuga.
- `crecimiento_esperado`: próximos 12 meses pronosticados contra los últimos 12 reales.

## App (`app/app.py`)
- Ranking de crecimiento esperado por región.
- Gráfica de demanda real + pronóstico por región, y tabla de los 12 meses.
- Total del SIN como suma de las 7 regiones (decisión de la Fase 6).
- `@st.cache_data(ttl=3600)`: consulta la base y entrena como máximo una vez por hora.
- No usa python-dotenv (dependencia de desarrollo); la variable llega por --env-file o por los secretos.

## Neon
- PostgreSQL 18, región AWS US East 2 (cerca de Streamlit Cloud).
- Conexión directa (no pooled): el pipeline hace TRUNCATE + carga en una transacción
  y la app consulta como máximo una vez por hora.
- URL con prefijo `postgresql+psycopg://` y `sslmode=require&channel_binding=require` (conexión cifrada).
- Credenciales en `.env.neon`, ignorado por git (regla `.env.*`).

## Streamlit Community Cloud
- `requirements.txt`: generado con `uv export --no-dev --no-hashes --format requirements-txt -o requirements.txt`.
  Incluye `-e .` para instalar el paquete del proyecto. Regenerarlo al cambiar dependencias.
- `packages.txt`: `libgomp1` (requisito de LightGBM a nivel sistema operativo).
- Python 3.12 (igual que en desarrollo; la opción por defecto era 3.14).
- DATABASE_URL en Secrets (formato TOML, valor entre comillas); Streamlit la expone como variable de entorno.

## Problemas encontrados
- Contraseña de Neon rechazada: se usó el usuario local `postgres` y luego una contraseña mal copiada.
  Solución: usuario `neondb_owner` y Reset password.
- Los errores "Network is unreachable" con direcciones IPv6 son inofensivos: WSL no tiene IPv6
  y psycopg prueba las direcciones IPv4.
- Secrets inválido: faltaban las comillas del valor TOML.
- Contraseña expuesta en una captura: se reseteó antes del despliegue.