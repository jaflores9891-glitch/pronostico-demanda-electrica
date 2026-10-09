## Limitaciones
- Sin temperatura: el modelo no puede anticipar un verano excepcional.
- Por qué importa: la demanda puede cambiar de forma importante por condiciones climáticas que no están representadas en los datos históricos de demanda. Por eso, una variación excepcional puede aparecer como atípica sin que el modelo tenga información para anticiparla.

## Conclusión del EDA
La demanda mensual presenta una estacionalidad marcada, pero con intensidad y meses pico diferentes entre regiones.  
El crecimiento también es regional: BCS muestra una tendencia de crecimiento más consistente, mientras que otras regiones presentan mayor variabilidad o desaceleración.  
Los meses atípicos deben conservarse, porque representan comportamiento real y no errores de datos.  
Para modelar será necesario considerar la estacionalidad (`lag_12`), los días del mes y la región, además de evaluar el error por región y no solo de forma global.