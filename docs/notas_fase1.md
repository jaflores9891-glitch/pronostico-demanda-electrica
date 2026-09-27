# Fase 1: Setup

**Fechas:** 26–27 de septiembre de 2026
**Resultado:** repositorio público con CI en verde, Postgres local y entorno reproducible.

---

## 1. Herramientas y versiones

| Herramienta | Versión | Para qué |
|---|---|---|
| Git | 2.53 | Control de versiones |
| uv | 0.12 | Python, entorno virtual y dependencias |
| Python | 3.12 (fijado en `.python-version`) | Lenguaje del proyecto |
| Ruff | dev | Linter y formateador |
| pytest | dev | Tests |
| Docker / Compose | 29.7 / v5.4 | Levantar Postgres local |
| PostgreSQL | 18 (`postgres:18`) | Base de datos; misma versión mayor que Neon |
| GitHub Actions | — | CI en cada push |

---

## 2. Pasos realizados

| Paso | Qué se hizo |
|---|---|
| 1.1 | Verificar herramientas; instalar uv con el instalador oficial (no snap) |
| 1.2 | `git init -b main` y `.gitignore` |
| 1.3 | `uv init --python 3.12` y `uv sync` |
| 1.4 | Estructura de carpetas; `git mv` de las notas a `docs/` |
| 1.5 | `uv add --dev ruff pytest`; smoke test |
| 1.6 | Postgres 18 con Docker Compose, `.env` y `.env.example` |
| 1.7 | Repositorio en GitHub y primer push por SSH |
| 1.8 | Workflow de CI con GitHub Actions |

---

## 3. Decisiones y por qué

### Entorno
- **Proyecto en `~` y no en `/mnt/c`:** en WSL es mucho más rápido y evita problemas de permisos.
- **uv con el instalador oficial:** snap depende de systemd, que no siempre está activo en WSL.
- **`uv run` en lugar de activar el entorno:** siempre usa el entorno del proyecto; es lo mismo que hace el CI.

### Reproducibilidad: se sube la receta, no el platillo
- **Se suben:** `pyproject.toml` (rangos compatibles), `uv.lock` (versiones exactas), `.python-version` (Python exacto).
- **No se suben:** `.venv/` (compilado para mi sistema) ni `data/raw/` (se regenera con el script).
- `requires-python = ">=3.12"` es un **rango**; `.python-version` **fija** la versión.
- Streamlit Cloud **no** lee `.python-version`: la versión se elige al desplegar (pendiente de la Fase 7).
- Dependencias de **producción** en `dependencies`; de **desarrollo** (Ruff, pytest) en `[dependency-groups] dev`.

### `.gitignore`
- `.env` y `.env.*` protegen secretos: un secreto subido queda en el historial aunque se borre.
- `!.env.example` va **después** de `.env.*`, porque Git lee de arriba hacia abajo.
- Git no guarda carpetas vacías.

### Tests
- **Smoke test:** verifica que el paquete se puede importar. Sin tests, pytest devuelve código 5 y el CI falla.
- **Un test que nunca puede fallar no prueba nada:** comprobé que falla (código 1) si escribo mal el paquete.
- **`assert` en lugar de `# noqa`:** el `assert` declara la intención; el `noqa` solo la esconde.
- **Trampa de `ruff check --fix`:** proponía reemplazar el import por `pass`, lo que habría dejado un test que siempre pasa. Las correcciones automáticas no se aplican a ciegas.

### Ruff: linter vs formateador
- `ruff check`: **linter**, busca errores y malas prácticas.
- `ruff format`: **formateador**, solo cambia el estilo, nunca la lógica.
- `--check` solo revisa sin modificar: es lo que usa el CI.

### Códigos de salida
| Código | Significado en pytest |
|---|---|
| 0 | Todos los tests pasaron |
| 1 | Algún test falló |
| 5 | No se encontró ningún test |

### PostgreSQL con Docker Compose
- **Postgres 18 = misma versión mayor que Neon**, para evitar diferencias entre local y producción.
- **`postgres:18` y no `latest`:** Postgres no puede leer datos guardados por otra versión mayor; con `latest`, una actualización dejaría el contenedor sin arrancar.
- **Volumen `postgres_data` en `/var/lib/postgresql`** (ruta correcta para Postgres 18). Comprobé la persistencia: creé una tabla, hice `docker compose down`, levanté de nuevo y el dato seguía ahí.
- **Nunca `docker compose down -v`**: borra los volúmenes y todos los datos.
- **Puerto 5433:** el 5432 de mi WSL ya estaba ocupado.
- **Mapeo de puertos `"${POSTGRES_PORT}:5432"`:** afuera, el puerto de mi computadora; adentro, Postgres siempre escucha en 5432. El contenedor está aislado, así que el conflicto solo existe afuera.
- **Credenciales en `.env`**, leídas por Compose con `${...}`. El puerto también, para tener una sola fuente de verdad.
- **Convenciones:** sin espacios alrededor del `=` en `.env`; nombres en minúsculas con guion bajo; evitar `user` porque es palabra reservada en SQL.
- **Servicio vs contenedor:** con `docker compose` se usa el servicio (`db`); el nombre del contenedor lo genera Docker.
- **Docker solo para Postgres:** Streamlit Cloud no acepta contenedores y el CI usa uv. Meter la app en Docker agregaría complejidad sin aportar.

### GitHub
- **Repositorio creado vacío:** un README, `.gitignore` o licencia creados por GitHub generarían un commit propio y dos historiales sin relación.
- **El push sube todo el historial**, lo que muestra cómo se construyó el proyecto.
- **Conexión por SSH** con llave protegida por passphrase.

### CI
- Corre en cada push a `main` y en cada pull request.
- Pasos: `uv sync --locked` → `ruff check` → `ruff format --check` → `pytest`.
- **`--locked`:** falla si `uv.lock` no coincide con `pyproject.toml`, para que el CI pruebe exactamente lo mismo que uso yo.
- **Las acciones de GitHub también se fijan.** `setup-uv` no publica etiquetas cortas como `v9`.
  Opción elegida: uses: astral-sh/setup-uv@bec219d24cd3e171d82865faccec33120bb574f4 # v10.1.0

---

## 4. Problemas encontrados

| Problema | Causa | Solución |
|---|---|---|
| `source ~/.local/bin/env` no existía | El instalador ya había agregado uv al PATH por otra vía | Ninguna; `uv --version` funcionaba |
| TOML inválido | Descripción partida en dos líneas | Un texto entre comillas no puede tener saltos de línea |
| Puerto 5432 ocupado | Otro programa lo usaba en WSL | Usar 5433 |
| YAML inválido | `ports` quedó dentro de `environment` por la sangría | Alinear al nivel correcto; verificar con `docker compose config` |
| pytest devolvía 5 | No había tests | Smoke test |
| Ruff F401 | Import sin usar en el test | `assert` sobre `__name__` |
| CI #1 en rojo | `setup-uv@v9` no existe | Fijar una versión exacta |
| CI #2 en rojo | El formato estaba corregido localmente, pero no en un commit | Commit del formato |

---

## 5. Comandos útiles

```bash
# Antes de cada push: los mismos chequeos que el CI
uv run ruff check . && uv run ruff format --check . && uv run pytest

# Postgres
docker compose up -d
docker compose ps
docker compose down          # sin -v
docker compose config        # valida el YAML (muestra la contraseña)
docker compose exec db psql -U postgres -d pronostico_demanda -c "SELECT version();"

# Git
git status                   # siempre antes de git add
git log --oneline            # si HEAD y origin/main difieren, falta un push
```

---

## 6. Pendientes

- [ ] Llenar los 3 `[COMPLETAR]` de `notas_fase0.md`
- [ ] Decidir si se agrega licencia (MIT)
- [ ] Fase 7: elegir Python 3.12 en la configuración de Streamlit Cloud

---

## 7. Preguntas de entrevista

**Cuéntame de una vez que algo falló en tu proyecto y cómo lo resolviste.**
Al configurar el CI con GitHub Actions, falló dos veces. La primera, porque referencié
una versión de la acción `setup-uv` que no existía; revisé el repositorio oficial y fijé
una versión exacta, igual que fijo Python y mis dependencias. La segunda, el paso de
formato detectó un archivo sin formatear: lo había corregido localmente, pero ese cambio
no estaba en un commit. Desde entonces, antes de cada push corro los mismos chequeos que el CI.

**¿Para qué sirve tu primer test si todavía no hay lógica?**
Antes de tener lógica de negocio, mi primer test verifica que la estructura básica del
proyecto funciona y que el paquete puede importarse. También comprobé que falla cuando
debe fallar.

**¿Por qué usas Docker solo para Postgres?**
Ver la sección 3.

**¿Por qué `uv sync --locked` en el CI?**
Ver la sección 3.