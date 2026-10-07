### Descarga manual por año (opción B)
- La página de CENACE es ASP.NET (POST con __VIEWSTATE y __EVENTVALIDATION).
  Automatizarla es complejo y puede romperse si CENACE cambia la página.
- Se descargan 5 .zip anuales a mano (~42 MB); Python hace el resto.
- Cada .zip trae las liquidaciones 0 a 4; solo se extrae la 0.
- Por qué: **son solo 5 archivos, se descargan en unos minutos y una sola vez. El valor del proyecto está en construir un pipeline reproducible a partir de los archivos crudos, no en automatizar el scraping de la página de CENACE.**

### Cambios de horario
- 368,063 filas (no 1,704 × 216 = 368,064) por días de 23 y 25 horas.
- BCA sigue el horario de EE. UU. (2.º domingo de marzo / 1.er domingo de noviembre).
- El resto de México cambió de horario por última vez en 2022 (03/04 y 30/10).
- CENACE numera la hora extra como 25.
- Decisión: conservar esos días. Por qué: **son datos reales del periodo y el objetivo es obtener la energía mensual, por lo que conservar las horas reales permite calcular el total correcto.**

### Recarga completa e idempotencia
- Llave primaria: (fecha, hora, sistema, area). Se comprobó que no hay duplicados.
- TRUNCATE + INSERT en una sola transacción.
- Correr el pipeline dos veces da el mismo resultado (368,063 filas).
- Por qué no upsert: **el pipeline reconstruye la tabla completa a partir de los archivos fuente; no necesita actualizar registros individuales. Con ~368 mil filas, la recarga completa tarda solo unos segundos y es más simple y reproducible.