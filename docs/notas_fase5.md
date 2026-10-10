# Notas de la Fase 5: Modelos

## Corrección al plan de la Fase 0: no usar lag_2
- El horizonte es de 12 meses. Para pronosticar ago-2026 desde ago-2025, el lag_2
  (jun-2026) todavía no existe: usarlo sería fuga de información.
- Solo se usan variables conocidas al momento del pronóstico: lag_12 o mayores.

## Diseño
- Objetivo: crecimiento interanual en logaritmo, log(gwh_dia / lag_12).
- Pronóstico final: lag_12 × e^(crecimiento) × días del mes.
- Ventajas: corrige la debilidad del naive estacional (asume crecimiento cero)
  y evita que LightGBM tenga que extrapolar niveles que nunca vio.
- Entrenamiento desde ene-2023 (2022 no tiene lag_12): 32 meses × 9 regiones = 288 filas.

## Archivos
- `features.py`: gwh_dia, lag_12, mes_del_anio, tendencia y log_crecimiento.
- `models.py`:
  - OLS (statsmodels): `log_crecimiento ~ C(region)` → crecimiento promedio por región.
  - LightGBM: region, mes_del_anio, tendencia y lag_12; parámetros conservadores
    (200 árboles, 7 hojas, learning_rate 0.05) por tener pocos datos.

## Resultados (WAPE en prueba, sep-2025 a ago-2026)
| Región | Naive estacional | OLS | LightGBM |
|---|---|---|---|
| BCA-BCA | 5.7 | 5.3 | 6.4 |
| BCS-BCA | 10.2 | 6.1 | 7.4 |
| SIN-CEN | 2.7 | 2.4 | 3.7 |
| SIN-NES | 3.8 | 3.4 | 4.1 |
| SIN-NOR | 7.0 | 5.4 | 7.1 |
| SIN-NTE | 4.4 | 5.0 | 5.3 |
| SIN-OCC | 2.8 | 1.5 | 3.5 |
| SIN-ORI | 3.3 | 2.3 | 3.2 |
| SIN-PEN | 4.3 | 6.1 | 4.7 |
| **Global** | **3.83** | **3.20** | **4.28** |

Crecimiento anual aprendido por el OLS: PEN 6.0%, BCS 5.7%, NOR 3.1%, ORI 2.5%,
OCC 1.8%, NES 1.8%, NTE 1.7%, BCA 1.2%, CEN 0.2%.

## Conclusiones
- Modelo elegido: OLS. Reduce el WAPE global 16% frente al naive y gana en 7 de 9 regiones.
- Mayor mejora en BCS (10.2% → 6.1%), la región con tendencia más fuerte.
- LightGBM pierde contra el naive: con 288 filas y años afectados por el clima, sobreajusta.
  Más complejidad no garantizó mejor pronóstico.
- El OLS pierde en PEN: proyecta su crecimiento promedio (6.0%) en un año en que casi no creció.
  Limitación: supone que el crecimiento pasado se mantiene.

## Limitaciones y mejoras futuras
- Evaluación con un solo periodo de prueba; una validación con varios cortes
  (TimeSeriesSplit) daría una estimación más robusta del error.
- Sin temperatura: no se pueden anticipar veranos excepcionales.
- El crecimiento promedio no capta desaceleraciones (PEN); se podría dar más peso
  a los años recientes.

## Requisitos del sistema (problemas encontrados)
- LightGBM necesita OpenMP del sistema operativo: `sudo apt-get install -y libgomp1`
  (error: `libgomp.so.1: cannot open shared object file`). En Streamlit Cloud se declara en `packages.txt`.
- `LGBMRegressor` requiere scikit-learn: `uv add scikit-learn`.
- Bug corregido en `naive_estacional`: el merge chocaba con la columna `gwh_dia`
  creada por `agregar_variables`; ahora solo usa region, mes y dias de `prueba`.