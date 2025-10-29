import pandas as pd
from pathlib import Path

#-------------------------------------------------
#BLOQUE 1 — Cargar el archivo original y revisar su tamaño
#-------------------------------------------------

# 📂 1️⃣ Definir la ruta donde está el archivo original
# (la carpeta "data" debe existir y dentro debe estar tu CSV original)
DATA_DIR = Path("data")
FILE_PATH = DATA_DIR / "Reporte_Hurto_por_Modalidades_Policía_Nacional.csv"

# 📥 2️⃣ Cargar el archivo en memoria usando pandas
# Se usa encoding UTF-8 para leer bien los caracteres (acentos, ñ, etc.)
df = pd.read_csv(FILE_PATH, encoding="utf-8", low_memory=False)

# 🧾 3️⃣ Mostrar cuántas filas (registros) y columnas tiene el archivo original
print("✅ Archivo cargado correctamente")
print("Número de filas (registros):", len(df))
print("Número de columnas:", len(df.columns))

# 👀 4️⃣ Ver los primeros registros para conocer cómo vienen los nombres de las columnas
print("\nPrimeras 5 filas del dataset original:")
print(df.head())


#-------------------------------------------------
#BLOQUE 2 — Limpiar los nombres de columnas
#-------------------------------------------------

# ✨ 5️⃣ Limpieza básica de nombres de columnas
# Convertimos los títulos de las columnas a minúsculas y quitamos espacios al inicio y final
df.columns = df.columns.str.lower().str.strip()

print("\n🧹 Nombres de columnas normalizados:")
print(df.columns.tolist())
print("Número de filas (registros):", len(df.columns))


#-------------------------------------------------
#BLOQUE 3 — Filtrar solo registros de Antioquia
#-------------------------------------------------

# 🏙️ 6️⃣ Filtrar los registros donde el departamento sea ANTIOQUIA
# Algunos registros pueden tener letras minúsculas o espacios, por eso usamos .str.contains
filtro_antioquia = df["departamento"].str.contains("ANTIOQUIA", case=False, na=False)

# Creamos una nueva base solo con esos registros
df_antioquia = df[filtro_antioquia].copy()

print("\n📊 Filtrado por departamento: ANTIOQUIA")
print("Registros originales:", len(df))
print("Registros después del filtro:", len(df_antioquia))
print("Registros eliminados:", len(df) - len(df_antioquia))


#-------------------------------------------------
#BLOQUE 4 — Normalizar el nombre del municipio y revisar datos faltantes
#-------------------------------------------------

# 🧩 7️⃣ Normalizar los nombres de municipios (todo en mayúsculas y sin espacios extras)
df_antioquia["municipio"] = df_antioquia["municipio"].str.upper().str.strip()

# 📉 8️⃣ Revisar si hay datos faltantes en campos importantes
print("\n📋 Revisión de valores nulos:")
print(df_antioquia[["departamento", "municipio", "fecha hecho"]].isna().sum())
print("Número de filas (registros):", len(df_antioquia))



#-------------------------------------------------
#BLOQUE 5 — Guardar el archivo limpio y mostrar los primeros resultados
#-------------------------------------------------

# 💾 10️⃣ Guardar el resultado limpio en un nuevo archivo CSV
OUT_FILE = DATA_DIR / "hurto_policia_limpio.csv"
df_antioquia.to_csv(OUT_FILE, index=False, encoding="utf-8-sig")

# 📤 11️⃣ Confirmar que se guardó correctamente
print(f"\n✅ Archivo limpio guardado como: {OUT_FILE}")
print("Número total de registros en el archivo limpio:", len(df_antioquia))

# 👀 12️⃣ Ver las primeras filas del archivo limpio
print("\nPrimeras 10 filas del dataset limpio:")
print(df_antioquia.head(10))
