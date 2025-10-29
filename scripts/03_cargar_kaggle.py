
import pandas as pd
from pathlib import Path

#-------------------------------------------------
# BLOQUE 1 — Cargar el archivo de Kaggle correctamente
#-------------------------------------------------

# 📂 1️⃣ Ruta del archivo
DATA_DIR = Path("data")
CSV_FILE = DATA_DIR / "robbery of people in Medellin.csv"

# 📄 2️⃣ Verificar que el archivo exista
if not CSV_FILE.exists():
    raise FileNotFoundError(f"❌ No se encontró el archivo: {CSV_FILE.resolve()}")
else:
    print(f"✅ Archivo encontrado: {CSV_FILE.name}")

# 🔍 3️⃣ Detectar si el separador es ',' o ';' o '\t'
with open(CSV_FILE, "r", encoding="utf-8", errors="ignore") as f:
    first_line = f.readline()
    if ";" in first_line:
        sep = ";"
    elif "\t" in first_line:
        sep = "\t"
    else:
        sep = ","

print(f"🧭 Separador detectado automáticamente: '{sep}'")

# 📥 4️⃣ Cargar el archivo con el separador correcto
try:
    df = pd.read_csv(CSV_FILE, sep=sep, encoding="utf-8", on_bad_lines="skip", low_memory=False)
except UnicodeDecodeError:
    df = pd.read_csv(CSV_FILE, sep=sep, encoding="latin-1", on_bad_lines="skip", low_memory=False)

print(f"✅ Archivo cargado correctamente ({len(df)} filas, {len(df.columns)} columnas)")



#-------------------------------------------------
#BLOQUE 2 — Limpiar los nombres de columnas
#-------------------------------------------------

# ✨ Pasar todos los nombres a minúsculas y quitar espacios
df.columns = df.columns.str.lower().str.strip()

print("\n🧹 Nombres de columnas normalizados:")
print(df.columns.tolist())


#-------------------------------------------------
#BLOQUE 3 — Detección automática de columnas clave
#-------------------------------------------------

# 🔍 Buscar columnas que coincidan con palabras comunes
col_fecha = next((c for c in df.columns if "fecha" in c), None)
col_barrio = next((c for c in df.columns if "barrio" in c), None)
col_sede = next((c for c in df.columns if "sede" in c), None)
col_conducta = next((c for c in df.columns if "conducta" in c), None)
col_modalidad = next((c for c in df.columns if "modalidad" in c), None)
col_bien = next((c for c in df.columns if "bien" in c and "categoria" not in c), None)
col_arma = next((c for c in df.columns if "arma" in c or "medio" in c), None)
col_transporte = next((c for c in df.columns if "transporte" in c), None)
col_sexo = next((c for c in df.columns if "sexo" in c), None)

# 📋 Mostrar resultados
print("\n📋 Columnas detectadas automáticamente:")
print(f"- Fecha: {col_fecha}")
print(f"- Barrio: {col_barrio}")
print(f"- Sede: {col_sede}")
print(f"- Conducta: {col_conducta}")
print(f"- Modalidad: {col_modalidad}")
print(f"- Bien: {col_bien}")
print(f"- Arma o Medio: {col_arma}")
print(f"- Medio de transporte: {col_transporte}")
print(f"- Sexo: {col_sexo}")


#-------------------------------------------------
# BLOQUE 4 — Convertir fechas y extraer año/mes
#-------------------------------------------------

if col_fecha:
    # Intentar conversión usando formato día/mes/año
    df[col_fecha] = pd.to_datetime(df[col_fecha], errors="coerce", dayfirst=True)

    # Mostrar rango temporal
    if df[col_fecha].notna().any():
        fecha_min = df[col_fecha].min()
        fecha_max = df[col_fecha].max()
        print(f"\n📅 Fechas convertidas correctamente.")
        print(f"📆 Los datos van desde {fecha_min.date()} hasta {fecha_max.date()}")
    else:
        print("⚠️ No se pudieron convertir las fechas. Revisa el formato del CSV.")

    # Extraer columnas auxiliares
    df["anio"] = df[col_fecha].dt.year
    df["mes"] = df[col_fecha].dt.month
else:
    print("⚠️ No se encontró una columna de fecha para procesar.")

#-------------------------------------------------
# BLOQUE 5 — Estadísticas generales y tendencias
#-------------------------------------------------

# 🏙️ Barrios con más casos
if col_barrio:
    print("\n🏘️ Barrios con más casos registrados:")
    print(df[col_barrio].value_counts().head(10))

# 🏢 Sedes con más casos
if col_sede:
    print("\n🏢 Sedes con más registros:")
    print(df[col_sede].value_counts().head(10))

# 🔫 Tipo de arma o medio más común
if col_arma:
    print("\n🔫 Tipo de arma o medio más frecuente:")
    print(df[col_arma].value_counts().head(5))

# 🚗 Medio de transporte más usado
if col_transporte:
    print("\n🚗 Medio de transporte más frecuente:")
    print(df[col_transporte].value_counts().head(5))

# 🧍‍♂️ Distribución por sexo
if col_sexo:
    print("\n🧍‍♀️ Distribución por sexo:")
    print(df[col_sexo].value_counts())

# ⚙️ Conductas o modalidades más comunes
if col_conducta:
    print("\n⚙️ Conductas más frecuentes:")
    print(df[col_conducta].value_counts().head(5))

if col_modalidad:
    print("\n📦 Modalidades más frecuentes:")
    print(df[col_modalidad].value_counts().head(5))

# 💰 Tipos de bienes más afectados
if col_bien:
    print("\n💰 Bienes más afectados:")
    print(df[col_bien].value_counts().head(5))


#-------------------------------------------------
# BLOQUE 6 — Promedios mensuales y anuales de casos
#-------------------------------------------------

# 📊 1️⃣ Verificar que tengamos columna de fecha
if "anio" in df.columns and "mes" in df.columns:
    
    # 🔢 Contar casos por año y mes
    casos_por_anio = df["anio"].value_counts().sort_index()
    casos_por_mes = df["mes"].value_counts().sort_index()
    
    print("\n📅 Casos registrados por año:")
    for anio, total in casos_por_anio.items():
        print(f" - {int(anio)}: {int(total):,} casos")

    print("\n🗓️ Casos registrados por mes (promedio global):")
    for mes, total in casos_por_mes.items():
        print(f" - Mes {int(mes)}: {int(total):,} casos")

    # 📉 Calcular promedio mensual y anual
    promedio_anual = casos_por_anio.mean()
    promedio_mensual = casos_por_mes.mean()

    print(f"\n📊 Promedio de casos por año: {promedio_anual:,.0f}")
    print(f"📆 Promedio de casos por mes: {promedio_mensual:,.0f}")

else:
    print("⚠️ No hay columnas de año o mes disponibles para calcular promedios.")

#-------------------------------------------------
# BLOQUE 7 — Tendencias más frecuentes (modo resumen)
#-------------------------------------------------
tendencias = {}

def tendencia(col, nombre, mostrar_segundo=False):
    """
    Guarda en el diccionario la tendencia más común de una columna.
    Si mostrar_segundo=True, también muestra la segunda categoría más frecuente.
    """
    if col and col in df.columns:
        conteo = df[col].value_counts()
        if len(conteo) > 0:
            valor_principal = conteo.index[0]
            # Si la tendencia principal es "No" o similar, renombramos
            if str(valor_principal).strip().lower() in ["no", "ninguna", "nan", "sin dato"]:
                valor_principal = "No especificadas"
                # Tomar la siguiente más frecuente (si existe)
                if len(conteo) > 1:
                    segundo = conteo.index[1]
                    tendencias[nombre] = f"{valor_principal} (más frecuente siguiente: {segundo})"
                    return
            tendencias[nombre] = valor_principal
        else:
            tendencias[nombre] = "Sin datos"
    else:
        tendencias[nombre] = "No encontrada"

# 🧠 Distinguir arma de transporte
col_arma_pura = next((c for c in df.columns if "arma" in c or ("medio" in c and "transporte" not in c)), None)
col_transporte_puro = next((c for c in df.columns if "transporte" in c), None)

# Calcular tendencias clave
tendencia(col_sexo, "Sexo más afectado")
tendencia(col_conducta, "Conducta más frecuente")
tendencia(col_modalidad, "Modalidad más común")
tendencia(col_arma_pura, "Arma o medio de agresión más usado", mostrar_segundo=True)
tendencia(col_transporte_puro, "Medio de transporte más usado")
tendencia(col_bien, "Bien más afectado")

# Mostrar resultados
print("\n📊 Tendencias generales observadas (finales):")
for clave, valor in tendencias.items():
    print(f" - {clave}: {valor}")

#-------------------------------------------------
# BLOQUE 8 — Guardar archivo limpio para análisis posteriores
#-------------------------------------------------
OUT_FILE = Path("data") / "robos_medellin_limpio.csv"
df.to_csv(OUT_FILE, index=False, encoding="utf-8-sig")

print(f"\n✅ Archivo final guardado correctamente como: {OUT_FILE}")
print(f"📦 Total de registros: {len(df)} filas y {len(df.columns)} columnas")