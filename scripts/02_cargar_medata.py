import pandas as pd
from pathlib import Path

#-------------------------------------------------
#BLOQUE 1 — Cargar el archivo original y revisar contenido
#-------------------------------------------------

# 📂 1️⃣ Definir la ruta del archivo original
DATA_DIR = Path("data")
FILE_PATH = DATA_DIR / "consolidado_cantidad_casos_criminalidad_en_comunas_por_año.csv"

# 📥 2️⃣ Cargar el archivo con pandas (intenta utf-8 y luego latin-1 si hay errores de acentos)
try:
    df = pd.read_csv(FILE_PATH, encoding="utf-8", low_memory=False)
except UnicodeDecodeError:
    df = pd.read_csv(FILE_PATH, encoding="latin-1", low_memory=False)

# 📊 3️⃣ Mostrar tamaño del archivo original
print("✅ Archivo cargado correctamente")
print("Número de filas (registros):", len(df))
print("Número de columnas:", len(df.columns))

#-------------------------------------------------
#BLOQUE 2 — Limpiar los nombres de columnas
#-------------------------------------------------

# ✨ 5️⃣ Normalizar los nombres de las columnas
df.columns = df.columns.str.lower().str.strip()

# 📋 6️⃣ Ver cómo quedaron las columnas
print("\n🧹 Nombres de columnas normalizados:")
print(df.columns.tolist())


#-------------------------------------------------
#BLOQUE 3 — Detectar columnas clave automáticamente
#-------------------------------------------------
# 🧩 7️⃣ Buscar las columnas más importantes automáticamente
col_comuna = next((c for c in df.columns if "comuna" in c), None)
col_casos = next((c for c in df.columns if "caso" in c or "cantidad" in c), None)
col_anio = next((c for c in df.columns if "año" in c or "anio" in c or "fecha" in c), None)

# ⚠️ 8️⃣ Validar detección
if not col_comuna or not col_casos or not col_anio:
    raise ValueError("❌ No se encontraron las columnas necesarias (comuna, casos, año o fecha).")

print("\n🧭 Columnas detectadas automáticamente:")
print(f"- Comuna: {col_comuna}")
print(f"- Casos: {col_casos}")
print(f"- Año o Fecha: {col_anio}")


#-------------------------------------------------
#BLOQUE 4 — Detectar correctamente los años sin eliminar registros válidos
#-------------------------------------------------

# 📆 9️⃣ Revisar si la columna de año tiene formato de fecha o número
if df[col_anio].dtype == "object":
    if df[col_anio].astype(str).str.contains("-|/").any():
        # Si tiene guiones o barras, es fecha completa → convertir a año
        df[col_anio] = pd.to_datetime(df[col_anio], errors="coerce").dt.year
        print("\n📅 Se detectó formato de fecha completa. Se extrajo solo el año.")
    else:
        # Si ya son números, solo convertir a tipo numérico
        df[col_anio] = pd.to_numeric(df[col_anio], errors="coerce").astype("Int64")
        print("\n📆 Se detectó formato numérico de año (no fecha).")

# ✅ Validar si hay registros sin año (solo informativo, no se borra nada)
faltantes = df[col_anio].isna().sum()
if faltantes > 0:
    print(f"⚠️ Hay {faltantes} registros sin año. Serán ignorados en los cálculos.")
else:
    print("✅ Todos los registros tienen año válido.")


#-------------------------------------------------
#BLOQUE 5 — Agrupar por comuna y año
#-------------------------------------------------

# 📊 🔟 Agrupar los casos por comuna y año
df_agrupado = (
    df.groupby([col_comuna, col_anio])[col_casos]
    .sum()
    .reset_index()
    .rename(columns={col_comuna: "comuna", col_anio: "anio", col_casos: "casos"})
)

print("\n📊 Dataset agrupado por comuna y año (primeras filas):")
print(df_agrupado.head(10))

#-------------------------------------------------
#BLOQUE 6 — Determinar rango de años disponibles
#-------------------------------------------------

# 📅 11️⃣ Calcular el rango de años del dataset
anio_min = int(df_agrupado["anio"].min())
anio_max = int(df_agrupado["anio"].max())

print(f"\n📆 Los datos cubren desde el año {anio_min} hasta el año {anio_max}")
print(f"Total de años analizados: {anio_max - anio_min + 1}")


#-------------------------------------------------
#BLOQUE 7 — Mostrar cantidad de casos totales por año
#-------------------------------------------------

# 📈 12️⃣ Agrupar solo por año para ver la tendencia general
resumen_anual = (
    df_agrupado.groupby("anio")["casos"]
    .sum()
    .reset_index()
    .sort_values("anio")
)

print("\n📈 Casos totales por año:")
print(resumen_anual)

print("\nResumen simplificado:")
for _, row in resumen_anual.iterrows():
    print(f" - {int(row['anio'])}: {int(row['casos']):,} casos")



#-------------------------------------------------
#BLOQUE 8 — Guardar el archivo limpio
#-------------------------------------------------

# 💾 13️⃣ Guardar el dataset limpio con todos los años (sin eliminar nada)
OUT_FILE = DATA_DIR / "criminalidad_comunas_limpio.csv"
df_agrupado.to_csv(OUT_FILE, index=False, encoding="utf-8-sig")

print(f"\n✅ Archivo limpio guardado como: {OUT_FILE}")
print("Número total de registros:", len(df_agrupado))
