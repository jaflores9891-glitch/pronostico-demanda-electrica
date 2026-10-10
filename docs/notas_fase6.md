# Notas de la Fase 6: SIN contra regiones

## Pregunta
Para la demanda total del SIN, ¿es más preciso pronosticar la serie agregada (directo)
o sumar los pronósticos de sus 7 regiones (suma de regiones)?

## Método
- SIN total = suma mensual de CEN, NES, NOR, NTE, OCC, ORI y PEN (56 meses).
- Mismo modelo (OLS de crecimiento anual) y mismo periodo de prueba (sep-2025 a ago-2026).
- Directo: OLS sobre la serie agregada.
- Suma de regiones: OLS de la Fase 5 por región, sumando las 7 del SIN mes a mes.

## Resultados (WAPE del SIN total)
| Método | WAPE |
|---|---|
| Naive estacional | 2.55% |
| OLS directo | 1.88% |
| OLS suma de regiones | 1.87% |

## Conclusiones
- Empate: 0.01 puntos de diferencia no es significativo con un año de prueba.
- Ambos mejoran ~27% frente al naive estacional.
- El error del total (1.9%) es menor que el de cada región (2-6%): los errores regionales se compensan.
- Decisión: usar la suma de regiones. Misma precisión, pero da el detalle por región,
  el total cuadra con la suma de sus partes (coherencia) y la app usa un solo modelo.   
