# 🛡️ Proyecto Final: Mapa de Seguridad y Riesgo - Valle de Aburrá

Este proyecto integra datos públicos sobre criminalidad, hurtos y arriendos en Medellín y el Valle de Aburrá, generando un mapa interactivo que muestra los niveles de riesgo por zonas, comunas y municipios.
El análisis combina fuentes oficiales (Policía Nacional, Alcaldía de Medellín, DANE, entre otras) y cálculos automáticos hechos con Python.

📂 Estructura del Proyecto
mapa_seguridad_medellin/
│
├── data/                # Datos limpios y archivos finales
│   ├── hurto_policia_limpio.csv
│   ├── robos_medellin_limpio.csv
│   ├── criminalidad_comunas_limpio.csv
│   ├── arriendos_limpio.csv
│   └── data_final.csv
│
├── scripts/             # Procesos de limpieza, unión y validación
│   ├── 01_cargar_policia.py
│   ├── 02_cargar_robos.py
│   ├── 03_cargar_comunas.py
│   ├── 04_cargar_arriendos.py
│   ├── 05_unir_y_riesgo.py
│   └── 06_validar_salida.py
│
├── web/                 # Interfaz web (mapa interactivo)
│   ├── index.html
│   ├── styles.css
│   ├── app.js
│   └── data_final.json
│
└── README.md            # Descripción general del proyecto


🧠 Scripts Principales
Script	Descripción
01_cargar_policia.py	Limpia y organiza los registros de la Policía Nacional
02_cargar_robos.py	Procesa datos de hurtos reportados en Medellín
03_cargar_comunas.py	Normaliza la información geográfica de comunas
04_cargar_arriendos.py	Analiza los valores promedio de arriendo por zona
05_unir_y_riesgo.py	Une todas las fuentes, calcula el índice de riesgo y exporta resultados
06_validar_salida.py	Verifica que la salida final sea coherente y completa
🌍 Visualización Web

Genera el archivo data_final.json ejecutando:

python scripts/05_unir_y_riesgo.py


Luego inicia un servidor local desde la carpeta web:

cd web
python -m http.server 8080


Abre el navegador en:
👉 http://localhost:8080

El mapa mostrará:

🏙️ Comunas y municipios del Valle de Aburrá

🚨 Niveles de riesgo calculados automáticamente

💰 Promedios de arriendo por zona

📊 Alertas visuales (verde = segura, rojo = alto riesgo)

📈 Indicadores Calculados
Indicador	Descripción
Promedio de casos	Media mensual de robos por comuna, barrio o municipio
Índice de riesgo	Escala normalizada (0 a 1) basada en número de casos
Nivel de riesgo	Clasificación automática: 💎 Diamante, 🥇 Oro, 🥈 Plata, 🥉 Bronce, 🧱 Cobre
Nivel de alerta	Colores de riesgo: 🚨 Roja, 🟠 Media, 🟢 Segura
Promedios de arriendo	Valores medios por tipo de inmueble (apartamento, casa, local)
📦 Salidas Generadas
Archivo	Descripción
data_final.csv	Consolidado para análisis en Power BI o Excel
data_final.json	Fuente de datos para el mapa interactivo