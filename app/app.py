import pandas as pd
import streamlit as st

from pronostico_demanda_electrica.models import crecimiento_esperado, pronosticar_futuro
from pronostico_demanda_electrica.queries import leer_demanda_mensual
from pronostico_demanda_electrica.storage import crear_engine

st.set_page_config(page_title="Pronóstico de demanda eléctrica", layout="wide")


@st.cache_data(ttl=3600)
def cargar_datos() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Lee la demanda mensual de la base y calcula el pronóstico de 12 meses."""
    mensual = leer_demanda_mensual(crear_engine())
    futuro = pronosticar_futuro(mensual)
    return mensual, futuro


mensual, futuro = cargar_datos()
crecimiento = crecimiento_esperado(mensual, futuro)
inicio = futuro["mes"].min().strftime("%m/%Y")
fin = futuro["mes"].max().strftime("%m/%Y")

st.title("Pronóstico mensual de demanda eléctrica por región")
st.caption(
    f"Datos: CENACE, demanda real por balance (liquidación 0). "
    f"Pronóstico: {inicio} a {fin}. Modelo: regresión OLS del crecimiento anual "
    f"(WAPE de 3.2% en prueba, contra 3.8% del naive estacional)."
)

st.subheader("Crecimiento esperado en los próximos 12 meses")
st.caption("Comparado con los últimos 12 meses reales.")
st.bar_chart(crecimiento.rename("Crecimiento (%)"))

st.subheader("Demanda mensual por región")
region = st.selectbox("Región", sorted(mensual["region"].unique()))
real = mensual[mensual["region"] == region].set_index("mes")["demanda_gwh"]
pronostico = futuro[futuro["region"] == region].set_index("mes")["pronostico_gwh"]
grafica = pd.concat({"Real (GWh)": real, "Pronóstico (GWh)": pronostico}, axis=1)
st.line_chart(grafica)

tabla = pronostico.round(1).rename("Pronóstico (GWh)").to_frame()
tabla.index = tabla.index.strftime("%Y-%m")
st.dataframe(tabla)

st.subheader("Total del Sistema Interconectado Nacional (SIN)")
regiones_sin = futuro["region"].str.startswith("SIN-")
total_sin = futuro[regiones_sin].groupby("mes")["pronostico_gwh"].sum()
st.metric(
    "Demanda pronosticada del SIN, próximos 12 meses", f"{total_sin.sum():,.0f} GWh"
)
st.caption("Suma de los pronósticos de las 7 regiones del SIN (ver Fase 6).")
