import streamlit as st
import pandas as pd
import datetime

# Cargar datos
df = pd.read_csv("demo_productividad_maquinas.csv")

st.set_page_config(page_title="Chat para Maquinas Circulares", layout="wide")
st.title("🤖 Chat de Monitoreo de Maquinas Vanguard Pai Lung")
st.caption("Consulta el estado y la productividad de tus Maquinas con lenguaje natural")
st.markdown("---")

# Procesador simple de preguntas
def responder_pregunta(pregunta):
    pregunta = pregunta.lower()

    if "productividad" in pregunta:
        for maquina in df['Maquina'].unique():
            if maquina.lower() in pregunta:
                datos = df[df['Maquina'].str.lower() == maquina.lower()]
                promedio = datos['ProductividadReal'].mean()
                return f"📈 La productividad promedio de la Maquina {maquina} es de **{promedio:.2f}** unidades."
        return "❓ Por favor especifica una Maquina."

    elif "más paro" in pregunta:
        total_paros = df.groupby('Maquina')['MINUTOS DE OTROS PAROS'].sum()
        maquina_max = total_paros.idxmax()
        return f"🛑 La Maquina con más minutos de paros fue **{maquina_max}** con **{total_paros.max()}** minutos."

    elif "caída de tela" in pregunta:
        total_caidas = df.groupby('Maquina')['MINUTOS CAÍDA DE TELA'].sum()
        maquina_top = total_caidas.idxmax()
        return f"⚠️ La Maquina con más caídas de tela fue **{maquina_top}** con **{total_caidas.max()}** minutos."

    elif "semana" in pregunta:
        palabras = pregunta.split()
        for palabra in palabras:
            if palabra.isdigit():
                semana = int(palabra)
                if semana in df['Semana'].values:
                    datos = df[df['Semana'] == semana]
                    resumen = datos.groupby('Maquina')['ProductividadReal'].mean().reset_index()
                    resultado = "📊 Productividad promedio en la semana " + str(semana) + ":\n"
                    for _, row in resumen.iterrows():
                        resultado += f"- {row['Maquina']}: {row['ProductividadReal']:.2f} unidades\n"
                    return resultado
        return "❓ Por favor especifica una semana (ej. semana 14)."

    return "🤖 Lo siento, aún no entiendo esa pregunta. Intenta preguntar sobre productividad, paros o caídas de tela."

# Chat
if "historial" not in st.session_state:
    st.session_state.historial = []

for mensaje in st.session_state.historial:
    with st.chat_message(mensaje["rol"]):
        st.markdown(mensaje["contenido"])

pregunta_usuario = st.chat_input("Haz una pregunta sobre las Maquinas...")

if pregunta_usuario:
    st.session_state.historial.append({"rol": "user", "contenido": pregunta_usuario})
    with st.chat_message("user"):
        st.markdown(pregunta_usuario)

    respuesta = responder_pregunta(pregunta_usuario)
    st.session_state.historial.append({"rol": "assistant", "contenido": respuesta})
    with st.chat_message("assistant"):
        st.markdown(respuesta)
