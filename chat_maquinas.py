import streamlit as st
import pandas as pd
import datetime

# Cargar datos
df = pd.read_csv("demo_productividad_maquinas.csv")

# Normalizar nombres de columnas
df.columns = [col.strip().lower() for col in df.columns]

# Calcular una columna estimada de productividad
df["productividadreal"] = (
    (df["fin vueltas"] - df["inicio vueltas"]) / (
        (pd.to_datetime(df["fecha fin / hora fin"]) - pd.to_datetime(df["fecha inicio / hora inicio"]))
        .dt.total_seconds() / 60
    )
).fillna(0)

# Configuración de la página
st.set_page_config(page_title="Chat para Máquinas Circulares", layout="wide")
st.title("🤖 Chat de Monitoreo de Máquinas Vanguard Pai Lung")
st.caption("Consulta el estado y la productividad de tus máquinas con lenguaje natural")
st.markdown("---")

# Procesador simple de preguntas
def responder_pregunta(pregunta):
    pregunta = pregunta.lower()

    if "productividad" in pregunta:
        for maquina in df['maquina'].unique():
            if maquina.lower() in pregunta:
                datos = df[df['maquina'].str.lower() == maquina.lower()]
                promedio = datos['productividadreal'].mean()
                return f"📈 La productividad promedio de la máquina {maquina} es de **{promedio:.2f}** unidades."
        return "❓ Por favor especifica una máquina."

    elif "más paro" in pregunta:
        total_paros = df.groupby('maquina')['minutos de otros paros'].sum()
        maquina_max = total_paros.idxmax()
        return f"🛑 La máquina con más minutos de paros fue **{maquina_max}** con **{total_paros.max()}** minutos."

    elif "caída de tela" in pregunta:
        total_caidas = df.groupby('maquina')['minutos caída de tela'].sum()
        maquina_top = total_caidas.idxmax()
        return f"⚠️ La máquina con más caídas de tela fue **{maquina_top}** con **{total_caidas.max()}** minutos."

    elif "semana" in pregunta:
        palabras = pregunta.split()
        for palabra in palabras:
            if palabra.isdigit():
                semana = int(palabra)
                if semana in df['semana'].values:
                    datos = df[df['semana'] == semana]
                    resumen = datos.groupby('maquina')['productividadreal'].mean().reset_index()
                    resultado = "📊 Productividad promedio en la semana " + str(semana) + ":\n"
                    for _, row in resumen.iterrows():
                        resultado += f"- {row['maquina']}: {row['productividadreal']:.2f} unidades\n"
                    return resultado
        return "❓ Por favor especifica una semana (ej. semana 14)."

    return "🤖 Lo siento, aún no entiendo esa pregunta. Intenta preguntar sobre productividad, paros o caídas de tela."

# Chat
if "historial" not in st.session_state:
    st.session_state.historial = []

for mensaje in st.session_state.historial:
    with st.chat_message(mensaje["rol"]):
        st.markdown(mensaje["contenido"])

pregunta_usuario = st.chat_input("Haz una pregunta sobre las máquinas...")

if pregunta_usuario:
    st.session_state.historial.append({"rol": "user", "contenido": pregunta_usuario})
    with st.chat_message("user"):
        st.markdown(pregunta_usuario)

    respuesta = responder_pregunta(pregunta_usuario)
    st.session_state.historial.append({"rol": "assistant", "contenido": respuesta})
    with st.chat_message("assistant"):
        st.markdown(respuesta)
