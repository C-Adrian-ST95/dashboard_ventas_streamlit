from bs4 import BeautifulSoup
import pandas as pd
import requests
import streamlit as st 
import plotly.express as px
import warnings

warnings.filterwarnings("ignore")

def formato_numero(valor, prefijo=" "):
    for unidad in ['', 'mil']:
        if valor < 1000:
            return f"{prefijo}{valor:.2f} {unidad}"
        valor /= 1000
    return f"{prefijo}{valor:.2f} millones"

st.set_page_config(
    page_title="Carlos Adrian - Analista de Datos",
    page_icon="📊",
    layout="centered",
)

st.title("Dashboard de Ventas :sunglasses:")

#url = "https://www.football-data.co.uk/spainm.php"
url = "https://ahcamachod.github.io/productos"

response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")
datos = pd.read_json(soup.pre.contents[0])
#tables = soup.find_all("table")
col1, col2 = st.columns(2)

st.markdown(
    """
    <style>
    .big-font {
        font-size:20px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Título con tamaño personalizado
st.markdown('<p class="big-font">Métrica personalizada</p>', unsafe_allow_html=True)
with col1:
    st.metric('Facturación', formato_numero(datos['Precio'].sum(),'COP '), border=True)
with col2:
    st.metric('Cantidad de Ventas', formato_numero(datos.shape[0]), border=True)

st.dataframe(datos, height=200, use_container_width=True)

code = '''def hello():
    print("Hello, Streamlit!")'''
st.code(code, language="python")

st.subheader("Analista de Datos | Python | SQL | Power BI")
st.write("Transformo datos en decisiones. Experta en análisis exploratorio, visualización y automatización.")

st.latex(r'''
    a + ar + a r^2 + a r^3 + \cdots + a r^{n-1} =
    \sum_{k=0}^{n-1} ar^k =
    a \left(\frac{1-r^{n}}{1-r}\right)
    ''')