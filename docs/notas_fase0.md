# Fase 0: Revisión de datos

**Fechas:** 25–26 de septiembre de 2026

---

## 1. Pregunta del proyecto

> ¿Cuánta energía demandará cada región del sistema eléctrico mes a mes en los
> próximos 12 meses, y cuáles crecerán más respecto al año anterior?

- La primera parte es el **pronóstico** (se mide con MAE y WAPE).
- La segunda parte es el **hallazgo** que se obtiene a partir del pronóstico.

---

## 2. Criterios de viabilidad

Los definí **antes** de revisar los datos, para no ajustarlos a lo que encontrara:

1. Al menos **36 meses continuos** de historia utilizable.
2. Menos del **10% de meses faltantes** por región.
3. **Formato consistente** en todo el periodo, o un mapeo claro entre versiones.
4. Excluir **2020 y 2021** (pandemia) por ser un cambio de régimen, no demanda normal.

**Por qué 36 meses:** el baseline "mismo mes del año anterior" consume 12 meses antes de
su primer pronóstico, y se necesitan otros 12 para evaluarlo en todas las estaciones.
Los modelos con `lag_12` además necesitan datos de entrenamiento antes del periodo de prueba.

---

## 3. Fuente evaluada 1: ISSSTE (descartada)

- **Dataset:** "Recetas de medicamentos efectivamente surtidas a la población
  derechohabiente", en datos.gob.mx.
- **Portal nuevo:** enero y marzo a julio de 2026 (falta febrero). 6 meses.
- **Portal histórico:** solo 2025, con un **formato distinto** al de 2026.
- **Total:** 18 meses, con un hueco y dos formatos.

**Decisión:** descartado. No cumple el criterio de 36 meses, el hueco de febrero pesa
mucho en una serie tan corta, y el cambio de formato agrega riesgo de inconsistencias.
El formato podría unificarse, pero no tiene sentido hacerlo sin suficiente historia.

---

## 4. Fuente elegida: CENACE

- **Reporte:** Estimación de la Demanda Real del Sistema, **por Balance**.
- **Ubicación:** CENACE → SIM → Reportes → Estimación de la Demanda Real
  (https://www.cenace.gob.mx/Paginas/SIM/Reportes/EstimacionDemandaReal.aspx)
- **Granularidad original:** un archivo por día, una fila por hora, sistema y área.

### ¿Por qué "por balance" y no "por retiros"?

- **Balance:** energía generada e inyectada a la red, menos las exportaciones.
  **Incluye** pérdidas técnicas y no técnicas.
- **Retiros:** suma de las compras de energía de las entidades que la retiran de la red.
  **Excluye** pérdidas.

**Argumento:** elegí balance porque representa la energía que el sistema realmente tiene
que generar, incluyendo pérdidas técnicas y no técnicas, lo cual es importante para
evitar desabasto. Además, depende menos de mediciones que se corrigen después, así que
el dato más reciente está menos sujeto a cambios por re-liquidaciones.

### ¿Qué versión (liquidación) se usa?

CENACE publica varias versiones del mismo día: la liquidación 0 (inicial) y
re-liquidaciones posteriores. Los días de 2022 tienen hasta la liquidación 4;
los días recientes solo tienen la 0. La página las lista de la liquidación 0 a la 4,
de la más antigua a la más reciente.

- La liquidación 0 se publica ~14 días después del día de operación.
- La liquidación 4 llega ~616 días después.
- **Diferencia medida entre liquidación 0 y 4:** 0.27% hora por hora; 0.0% en el total anual.
- **Método:** comparé ambas liquidaciones en todo 2022 (78,840 registros: mismo día, sistema,
  área y hora). Diferencia hora por hora = Σ|L4 − L0| / Σ L0; diferencia total = Σ L4 / Σ L0 − 1.
  Las correcciones se compensan al sumar, así que el total mensual casi no cambia.

**Decisión:** usar siempre la **liquidación 0**.

**Argumento:** cuando el modelo pronostique en la vida real, los meses más recientes
solo existirán como liquidación 0.

---

## 5. Resultado de la revisión

| Criterio | Resultado con CENACE |
|---|---|
| ≥ 36 meses continuos | ✅ 56 meses (ene-2022 a ago-2026) |
| < 10% de meses faltantes | ✅ 0%: los 1,704 días completos en las 9 regiones |
| Formato consistente | ✅ con mapeo: 18 archivos de ago-2022 con nombres alternativos de columnas (ver Fase 2) |
| Sin pandemia | ✅ los datos empiezan en 2022 |

**Decisión:** CENACE cumple los cuatro criterios. Se usa de enero de 2022 a agosto de 2026.