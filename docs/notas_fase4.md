# Notas de la Fase 4: Baselines

## Separación temporal
- Entrenamiento: ene-2022 a ago-2025 (44 meses, 396 filas).
- Prueba: sep-2025 a ago-2026 (12 meses, 108 filas).
- 12 meses = horizonte del proyecto y un ciclo estacional completo.
- Nunca al azar: evita fuga de información del futuro.

## Métricas (`metrics.py`)
- MAE (GWh): tamaño absoluto del error.
- WAPE (%): error total / demanda total; compara regiones de distinto tamaño.
- `evaluar_por_region`: MAE y WAPE por región.

## Baselines (`baselines.py`)
- Ambos pronostican GWh/día × días del mes (evita el efecto calendario).
- Promedio de 12 meses: ignora la estacionalidad.
- Naive estacional: repite el mismo mes del año anterior.

## Resultados (WAPE)
| Región | Promedio 12 | Naive estacional |
|---|---|---|
| BCA-BCA | 19.6 | 5.7 |
| BCS-BCA | 19.0 | 10.2 |
| SIN-CEN | 2.9 | 2.7 |
| SIN-NES | 15.1 | 3.8 |
| SIN-NOR | 23.8 | 7.0 |
| SIN-NTE | 16.9 | 4.4 |
| SIN-OCC | 4.5 | 2.8 |
| SIN-ORI | 8.2 | 3.3 |
| SIN-PEN | 13.7 | 4.3 |
| **Global** | **10.72** | **3.83** |

## Conclusiones
- La estacionalidad es lo más importante: el naive estacional gana en las 9 regiones.
- SIN-CEN casi empata porque su perfil estacional es plano.
- BCS tiene el mayor error del naive (10.2%) por su tendencia de ~12% anual.
- Marca a superar en la Fase 5: WAPE global 3.83% y la columna del naive por región.
- El WAPE global está dominado por las regiones grandes; revisar también por región.