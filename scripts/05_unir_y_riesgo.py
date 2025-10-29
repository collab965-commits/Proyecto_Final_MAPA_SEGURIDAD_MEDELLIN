import pandas as pd
from pathlib import Path
import unicodedata

#-------------------------------------------------
# BLOQUE 1 — Cargar archivos y preparar entorno
#-------------------------------------------------

# 📂 Definir las rutas de los archivos
DATA_DIR = Path("data")
OUT_CSV = DATA_DIR / "data_final.csv"
OUT_JSON = Path("web") / "data_final.json"

# Archivos que vamos a usar
FILES = {
    "policia": DATA_DIR / "hurto_policia_limpio.csv",
    "robos": DATA_DIR / "robos_medellin_limpio.csv",
    "comunas": DATA_DIR / "criminalidad_comunas_limpio.csv",
    "arriendos": DATA_DIR / "arriendos_limpio.csv"
}

# 📥 Función para cargar cualquier CSV automáticamente
def cargar_csv(path):
    sep = ";" if ";" in open(path, "r", encoding="utf-8").read(2000) else ","
    df = pd.read_csv(path, sep=sep, encoding="utf-8")
    df.columns = df.columns.str.lower().str.strip()
    print(f"✅ {path.name} cargado correctamente: {df.shape[0]} filas, {df.shape[1]} columnas")
    return df

# Cargar todos los datasets
policia = cargar_csv(FILES["policia"])
robos = cargar_csv(FILES["robos"])
comunas = cargar_csv(FILES["comunas"])
arriendos = cargar_csv(FILES["arriendos"])

#-------------------------------------------------
# BLOQUE 2 — Normalizar texto y detectar columnas de ubicación
#-------------------------------------------------

# ✨ Función para limpiar texto y dejarlo uniforme
def limpiar_texto(serie):
    return (
        serie.astype(str)
        .str.upper()
        .apply(lambda x: unicodedata.normalize("NFKD", x))
        .str.encode("ascii", errors="ignore")
        .str.decode("utf-8")
        .str.replace(r"[^A-Z0-9 ]", "", regex=True)
        .str.strip()
    )

# 🔍 Detectar columnas relacionadas con ubicación (municipio, comuna, etc.)
def detectar_columnas_geo(df):
    columnas = [c for c in df.columns if any(k in c for k in ["departamento", "municipio", "comuna", "sector", "barrio", "codigo"])]
    print(f"📍 Columnas geográficas detectadas: {columnas}")
    return columnas

# Aplicar limpieza a todas las columnas de texto que sean geográficas
for df in [policia, robos, comunas, arriendos]:
    columnas_geo = detectar_columnas_geo(df)
    for c in columnas_geo:
        df[c] = limpiar_texto(df[c])

#-------------------------------------------------
# BLOQUE 3 — Calcular promedios y totales de robos por nivel
#-------------------------------------------------

print("\n📊 Calculando promedios y totales por nivel geográfico...")

# Buscar columna de fecha
col_fecha = next((c for c in robos.columns if "fecha" in c), None)
if col_fecha:
    robos[col_fecha] = pd.to_datetime(robos[col_fecha], errors="coerce")
    robos["mes"] = robos[col_fecha].dt.to_period("M")

# Identificar niveles geográficos posibles
niveles = [c for c in robos.columns if any(x in c for x in ["barrio", "comuna", "sector", "municipio"])]

# Crear lista vacía para guardar los resultados de cada nivel
resultados_niveles = []

# Recorremos cada nivel y calculamos sus totales y promedios
for nivel in niveles:
    print(f"📍 Procesando nivel: {nivel}")
    
    # Agrupar por mes y nivel para contar los robos
    if "mes" in robos.columns:
        datos = robos.groupby([nivel, "mes"]).size().reset_index(name="robos_mes")
        
        # Promedio mensual por nivel
        promedios = (
            datos.groupby(nivel)["robos_mes"]
            .mean()
            .reset_index(name="promedio_robos")
        )
        
        # Total de casos por nivel
        totales = robos.groupby(nivel).size().reset_index(name="casos_totales")
        
        # Unimos los dos resultados
        resumen = pd.merge(promedios, totales, on=nivel, how="outer")
        resumen["nivel_geo"] = nivel  # Guardamos el tipo de nivel (barrio, comuna, etc.)
        
        resultados_niveles.append(resumen)
        print(f"✅ Calculado correctamente para: {nivel}")

# Unir todos los niveles en un solo DataFrame
df_niveles = pd.concat(resultados_niveles, ignore_index=True)

print(f"\n✅ Consolidado de niveles generado: {df_niveles.shape[0]} filas, {df_niveles.shape[1]} columnas")
#-------------------------------------------------
# BLOQUE 4 — Promedios de la Policía Nacional
#-------------------------------------------------

print("\n🚓 Calculando promedios y totales de la Policía Nacional...")

# Buscar columnas principales
col_fecha_pol = next((c for c in policia.columns if "fecha" in c), None)
col_cant_pol = next((c for c in policia.columns if "cantidad" in c), None)
col_muni_pol = next((c for c in policia.columns if "municipio" in c), None)
col_depto_pol = next((c for c in policia.columns if "departamento" in c), None)

# Validar columnas encontradas
if not all([col_fecha_pol, col_cant_pol, col_muni_pol]):
    print("⚠️ No se encontraron todas las columnas necesarias en el dataset de Policía.")
else:
    # Convertir fecha a formato datetime
    policia[col_fecha_pol] = pd.to_datetime(policia[col_fecha_pol], errors="coerce")
    policia["mes"] = policia[col_fecha_pol].dt.to_period("M")

    # Agrupar por municipio y mes para calcular total de casos por mes
    resumen_mes = (
        policia.groupby([col_muni_pol, "mes"])[col_cant_pol]
        .sum()
        .reset_index(name="casos_mes")
    )

    # Calcular promedio mensual por municipio
    promedio_mensual = (
        resumen_mes.groupby(col_muni_pol)["casos_mes"]
        .mean()
        .reset_index(name="promedio_robos_municipio")
    )

    # Calcular total de casos en todo el periodo
    totales_muni = (
        policia.groupby(col_muni_pol)[col_cant_pol]
        .sum()
        .reset_index(name="casos_municipio")
    )

    # Unir ambos resultados
    policia_final = promedio_mensual.merge(totales_muni, on=col_muni_pol, how="outer")

    # Si hay columna de departamento, mantenerla para contexto
    if col_depto_pol in policia.columns:
        policia_final[col_depto_pol] = policia[col_depto_pol].mode()[0]

    print(f"✅ Policía procesada correctamente: {policia_final.shape[0]} municipios.")

#-------------------------------------------------
# BLOQUE 5 — Integrar información de arriendos
#-------------------------------------------------

print("\n🏘️ Integrando información de arriendos...")

# 🔍 1️⃣ Detectar columnas de ubicación (automático)
cols_geo_arr = [c for c in arriendos.columns if any(x in c for x in ["sector", "comuna", "municipio", "barrio"])]
print(f"📍 Columnas geográficas en arriendos: {cols_geo_arr}")

# 💰 2️⃣ Detectar columnas de valores de arriendo (promedios y rangos)
cols_valores = [c for c in arriendos.columns if any(x in c for x in ["promedio", "rango"])]
print(f"💰 Columnas de valores de arriendo: {cols_valores}")

# 🧹 3️⃣ Limpiar texto en columnas geográficas
for c in cols_geo_arr:
    arriendos[c] = (
        arriendos[c]
        .astype(str)
        .str.upper()
        .str.normalize("NFKD")
        .str.encode("ascii", errors="ignore")
        .str.decode("utf-8")
        .str.strip()
    )

# 🧩 4️⃣ Crear una columna de zona única para poder unir más adelante
def crear_zona_clave(df):
    """
    Crea una clave única combinando sector, comuna o municipio.
    Si un valor no existe, usa el siguiente disponible.
    """
    def construir(fila):
        sector = str(fila.get("sector", "")).strip()
        comuna = str(fila.get("comuna", "")).strip()
        muni = str(fila.get("municipio", "")).strip()
        barrio = str(fila.get("barrio", "")).strip()

        # Evitar 'nan' o vacíos
        for v in [sector, comuna, muni, barrio]:
            if v.lower() in ["nan", "none", "<na>", "sin info"]:
                v = ""

        # Priorizar orden lógico
        if barrio:
            return f"{muni}|BAR_{barrio}"
        if sector:
            return f"{muni}|SEC_{sector}"
        if comuna:
            return f"{muni}|COM_{comuna}"
        if muni:
            return muni
        return "SIN_INFO"

    df["zona_clave"] = df.apply(construir, axis=1)
    print(f"✅ Zona clave creada para {df['zona_clave'].nunique()} zonas únicas.")
    return df

# 🏷️ 5️⃣ Crear zona clave en arriendos
arriendos_final = crear_zona_clave(arriendos)

# 🧾 6️⃣ Conservar solo columnas relevantes
cols_finales = cols_geo_arr + cols_valores + ["zona_clave"]
arriendos_final = arriendos_final[cols_finales].copy()

print(f"✅ Arriendos listos: {arriendos_final.shape[0]} registros y {arriendos_final.shape[1]} columnas.")

#-------------------------------------------------
# BLOQUE 6 — Crear una llave única para unir todos los datasets
#-------------------------------------------------

print("\n🧭 Creando columna única de zona...")

def crear_zona_clave(df):
    def construir_llave(fila):
        dept = str(fila.get("departamento", "")).strip()
        muni = str(fila.get("municipio", "")).strip()
        com = str(fila.get("comuna", "")).strip()
        bar = str(fila.get("barrio", "")).strip()
        sec = str(fila.get("sector", "")).strip()

        # Reemplazar valores vacíos o no válidos
        valores = [dept, muni, com, bar, sec]
        valores = ["" if v.lower() in ["nan", "<na>", "none"] else v for v in valores]
        dept, muni, com, bar, sec = valores

        if com:
            return f"{dept}|{muni}|COM_{com}"
        if bar:
            return f"{dept}|{muni}|BAR_{bar}"
        if sec:
            return f"{dept}|{muni}|SEC_{sec}"
        if muni:
            return f"{dept}|{muni}"
        return "SIN_INFO"

    df["zona_clave"] = df.apply(construir_llave, axis=1)
    print(f"📍 Zonas únicas generadas: {df['zona_clave'].nunique()}")
    return df

# Crear la llave en todos los conjuntos
df_niveles = crear_zona_clave(df_niveles)
policia_final = crear_zona_clave(policia_final)
arriendos_final = crear_zona_clave(arriendos_final)

#-------------------------------------------------
# BLOQUE 7 — Unificación y cálculo del índice de riesgo
#-------------------------------------------------

print("\n🔗 Unificando información y calculando índice de riesgo...")

# Unir por zona_clave
df_union = df_niveles.merge(policia_final, on="zona_clave", how="outer").merge(arriendos_final, on="zona_clave", how="left")

# Calcular índice de riesgo
col_ref = next((c for c in df_union.columns if "promedio_robos" in c), None)
if col_ref:
    df_union["indice_riesgo"] = df_union[col_ref] / df_union[col_ref].max()
else:
    df_union["indice_riesgo"] = 0

# Clasificar niveles de riesgo
q20, q40, q60, q80 = df_union["indice_riesgo"].quantile([0.2, 0.4, 0.6, 0.8])

def clasificar_nivel(valor):
    if pd.isna(valor):
        return "Sin datos"
    if valor <= q20:
        return "💎 Diamante"
    elif valor <= q40:
        return "🥇 Oro"
    elif valor <= q60:
        return "🥈 Plata"
    elif valor <= q80:
        return "🥉 Bronce"
    else:
        return "🧱 Cobre"

def clasificar_alerta(nivel):
    if nivel in ["🧱 Cobre", "🥉 Bronce"]:
        return "🚨 Alerta Roja"
    elif nivel == "🥈 Plata":
        return "🟠 Alerta Media"
    elif nivel in ["🥇 Oro", "💎 Diamante"]:
        return "🟢 Segura"
    return "Sin datos"

df_union["nivel_riesgo"] = df_union["indice_riesgo"].apply(clasificar_nivel)
df_union["alerta"] = df_union["nivel_riesgo"].apply(clasificar_alerta)

print("✅ Índice de riesgo calculado correctamente.")

#-------------------------------------------------
# BLOQUE 8 — Exportar archivos finales
#-------------------------------------------------

print("\n💾 Exportando resultados...")

df_union.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
df_union.to_json(OUT_JSON, orient="records", force_ascii=False, indent=2)

print(f"✅ Archivos generados correctamente:")
print(f"   📄 CSV:  {OUT_CSV}")
print(f"   🌐 JSON: {OUT_JSON}")

#-------------------------------------------------
# BLOQUE 9 — Mostrar ejemplo de salida
#-------------------------------------------------

def formato_dinero(valor):
    if pd.isna(valor):
        return "Sin datos"
    return f"${int(valor):,}".replace(",", ".")

def mostrar_resumen(fila):
    return f"""
📍 Zona: {fila.get('zona_clave', 'Sin info')}
⚠️ Nivel de riesgo: {fila.get('nivel_riesgo', 'Sin datos')} — {fila.get('alerta', 'Sin alerta')}
📊 Promedio mensual: {round(fila.get('indice_riesgo', 0)*100, 2)}%
💰 Arriendo promedio:
   🏢 Apartamento: {formato_dinero(fila.get('promedio_arriendo_apartamento'))}
   🏠 Casa: {formato_dinero(fila.get('promedio_arriendo_casa'))}
   🏪 Local: {formato_dinero(fila.get('promedio_arriendo_local'))}
"""

if not df_union.empty:
    print("\n🧾 Ejemplo de salida:")
    print(mostrar_resumen(df_union.iloc[0]))
else:
    print("⚠️ No hay registros para mostrar.")