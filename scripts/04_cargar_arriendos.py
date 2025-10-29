import pandas as pd
from pathlib import Path
#-------------------------------------------------
#BLOQUE 1 — Cargar archivo y explorar datos básicos
#-------------------------------------------------
# Ruta base de datos
DATA_DIR = Path("data")
ARCHIVO = DATA_DIR / "arriendos_valle_aburra_2025.csv"
SALIDA = DATA_DIR / "arriendos_limpio.csv"

# Verificar que el archivo existe
if not ARCHIVO.exists():
    raise FileNotFoundError(f"❌ No se encontró el archivo: {ARCHIVO.resolve()}")

# Intentar detectar el separador automáticamente
with open(ARCHIVO, "r", encoding="utf-8") as f:
    muestra = f.read(2000)

sep = ";" if ";" in muestra else ","

# Cargar el archivo
df = pd.read_csv(ARCHIVO, sep=sep, encoding="utf-8")
print(f"✅ Archivo cargado correctamente: {df.shape[0]} filas y {df.shape[1]} columnas")

# Normalizar nombres de columnas (todo en minúsculas y sin espacios)
df.columns = df.columns.str.lower().str.strip()


#-------------------------------------------------
#BLOQUE 2 — Detectar columnas de ubicación y precios automáticamente
#-------------------------------------------------

# Detectar ubicación
col_sector = next((c for c in df.columns if "sector" in c), None)
col_comuna = next((c for c in df.columns if "comuna" in c), None)
col_municipio = next((c for c in df.columns if "municipio" in c), None)

# Detectar precios y rangos
cols_precios = [c for c in df.columns if "promedio" in c or "rango" in c or "precio" in c]

# Mostrar detección
print("\n🔍 Columnas detectadas automáticamente:")
print(f"- Sector: {col_sector}")
print(f"- Comuna: {col_comuna}")
print(f"- Municipio: {col_municipio}")
print(f"- Columnas de precios o rangos: {cols_precios}")

# Limpiar texto en columnas de ubicación
for col in [col_sector, col_comuna, col_municipio]:
    if col in df.columns:
        df[col] = df[col].astype(str).str.upper().str.strip()



#-------------------------------------------------
#BLOQUE 3 — Normalizar y convertir valores numéricos
#-------------------------------------------------


# Convertir todas las columnas de precios a formato numérico
for col in cols_precios:
    if col in df.columns:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace("[^0-9,.-]", "", regex=True)
            .str.replace(",", ".", regex=False)
        )
        df[col] = pd.to_numeric(df[col], errors="coerce")

print("\n💰 Conversión numérica completada.")

#-------------------------------------------------
#BLOQUE 4 — Calcular promedios por nivel geográfico y tipo de arriendo
#-------------------------------------------------
# Detección automática de tipos de arriendo
tipos_arriendo = ["apartamento", "casa", "local"]

niveles = {
    "sector": col_sector,
    "comuna": col_comuna,
    "municipio": col_municipio
}

# Para cada nivel geográfico (sector, comuna, municipio)
for nombre, col in niveles.items():
    if col:
        print(f"\n📈 Promedios de arriendo por {nombre.upper()}:")

        # Buscar dinámicamente las columnas asociadas a cada tipo
        for tipo in tipos_arriendo:
            cols_tipo = [c for c in cols_precios if tipo in c]
            if not cols_tipo:
                continue

            # Agrupar y calcular promedios
            promedio = df.groupby(col)[cols_tipo].mean().round(2)

            print(f"\n🏠 {tipo.capitalize()}:")
            print(promedio.head(10))
            
#-------------------------------------------------
#BLOQUE 5 — Guardar el archivo limpio
#-------------------------------------------------
# Seleccionar solo las columnas válidas detectadas
cols_finales = [c for c in [col_sector, col_comuna, col_municipio] if c] + cols_precios
df_final = df[cols_finales].copy()

# Guardar
df_final.to_csv(SALIDA, index=False, encoding="utf-8-sig")

print(f"\n✅ Archivo limpio guardado correctamente en: {SALIDA}")
print(f"📊 Total de registros: {df_final.shape[0]} filas y {df_final.shape[1]} columnas")