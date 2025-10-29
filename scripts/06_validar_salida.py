import pandas as pd
from pathlib import Path

# 📂 Cargar archivo final generado en el paso anterior
DATA_DIR = Path("data")
OUT_FILE = DATA_DIR / "data_final.csv"

# ✅ 1️⃣ Leer el archivo
df = pd.read_csv(OUT_FILE, encoding="utf-8-sig")
print(f"✅ Archivo cargado correctamente: {OUT_FILE.name}")
print(f"📏 Dimensiones: {df.shape[0]} filas × {df.shape[1]} columnas")

# ✅ 2️⃣ Mostrar resumen general
print("\n📋 Columnas disponibles:")
for c in df.columns:
    print(" -", c)

# ✅ 3️⃣ Mostrar las primeras filas
print("\n🔍 Ejemplo de datos (primeras 5 filas):")
print(df.head(5))

# ✅ 4️⃣ Verificar columnas críticas
cols_clave = [c for c in df.columns if any(x in c for x in ["zona", "municipio", "comuna", "sector", "barrio"])]
cols_riesgo = [c for c in df.columns if "riesgo" in c or "alerta" in c]
cols_arriendo = [c for c in df.columns if "arriendo" in c]

print("\n🧭 Columnas de ubicación detectadas:", cols_clave)
print("⚠️ Columnas de riesgo detectadas:", cols_riesgo)
print("💰 Columnas de arriendo detectadas:", cols_arriendo)

# ✅ 5️⃣ Validar valores nulos
print("\n🚦 Resumen de valores faltantes (top 10 columnas con más vacíos):")
print(df.isna().sum().sort_values(ascending=False).head(10))

# ✅ 6️⃣ Resumen de riesgo
if "nivel_riesgo" in df.columns:
    print("\n🏅 Distribución de niveles de riesgo:")
    print(df["nivel_riesgo"].value_counts(dropna=False))
else:
    print("\n⚠️ No se encontró la columna 'nivel_riesgo' en el archivo final.")

# ✅ 7️⃣ Promedio general de arriendos
cols_prom = [c for c in df.columns if "promedio_arriendo" in c]
if cols_prom:
    print("\n💰 Promedios generales de arriendo (valores aproximados):")
    print(df[cols_prom].mean(numeric_only=True).round(0))
else:
    print("\n⚠️ No hay columnas de promedio de arriendo detectadas.")

# ✅ 8️⃣ Ejemplo detallado (primer registro con valores no nulos)
ejemplo = df.dropna(subset=["zona_clave"]).iloc[0]
print("\n🧾 Ejemplo de registro válido:")
for k, v in ejemplo.items():
    print(f"   {k}: {v}")