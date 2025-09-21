from bs4 import BeautifulSoup
import pandas as pd
import requests
import streamlit as st 
import time 
import warnings

warnings.filterwarnings("ignore")

@st.cache_data
def convierte_csv(df):
    return df.to_csv(index=False,sep='#').encode('utf-8')

def mensaje_exito():
    exito = st.success("¡Datos descargados con éxito!", icon="✅")
    time.sleep(2)
    exito.empty()


st.title("Datos Brutos :mag:")
url = "https://ahcamachod.github.io/productos"

response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")
datos = pd.read_json(soup.pre.contents[0])
datos['Fecha de Compra'] = pd.to_datetime(datos['Fecha de Compra'], format='%d/%m/%Y')  



st.sidebar.title('Filtros')

with st.sidebar.expander("Categoría del Producto"):
    categoria = st.multiselect('Seleccione la Categoría', datos['Categoría del Producto'].unique(), list(datos['Categoría del Producto'].unique())) 
    datos = datos[datos['Categoría del Producto'].isin(categoria)]


with st.sidebar.expander("Nombre del Producto"):
    Producto = st.multiselect('Seleccione el Producto', datos['Producto'].unique(), list(datos['Producto'].unique())) 
    datos = datos[datos['Producto'].isin(Producto)]

with st.sidebar.expander("Precio del Producto"):
    Precio = st.slider('Seleccione el Rango de Precio', min_value=0, max_value=int(datos['Precio'].max()), value=(0, int(datos['Precio'].max())))
    datos = datos[(datos['Precio'] >= Precio[0]) & (datos['Precio'] <= Precio[1])]

with st.sidebar.expander("Fecha de Compra"):
    fecha_inicio = st.date_input('Fecha de Inicio', value=datos['Fecha de Compra'].min())
    fecha_fin = st.date_input('Fecha de Fin', value=datos['Fecha de Compra'].max()) 
    datos = datos[(datos['Fecha de Compra'] >= pd.to_datetime(fecha_inicio)) & (datos['Fecha de Compra'] <= pd.to_datetime(fecha_fin))] 


with st.sidebar.expander("Costo de envío"):
    frete = st.slider('Seleccione el Rango de Costo de envío', min_value=0, max_value=int(datos['Costo de envío'].max()), value=(0, int(datos['Costo de envío'].max())))
    datos = datos[(datos['Costo de envío'] >= frete[0]) & (datos['Costo de envío'] <= frete[1])]

with st.sidebar.expander("Vendedores"):
    vendedores = st.multiselect('Seleccione los Vendedores', datos['Vendedor'].unique(), list(datos['Vendedor'].unique())) 
    datos = datos[datos['Vendedor'].isin(vendedores)]

with st.sidebar.expander("Lugar de Compra"):
    local_compra = st.multiselect('Seleccione el Lugar de Compra', datos['Lugar de Compra'].unique(), list(datos['Lugar de Compra'].unique())) 
    datos = datos[datos['Lugar de Compra'].isin(local_compra)]  


with st.sidebar.expander("Método de pago"):
    tipo_pagamento = st.multiselect('Seleccione el Método de pago', datos['Método de pago'].unique(), list(datos['Método de pago'].unique())) 
    datos = datos[datos['Método de pago'].isin(tipo_pagamento)]

with st.sidebar.expander("Cantidad de cuotas"):
    qtd_parcelas = st.slider('Seleccione el Rango de Cantidad de cuotas', min_value=1, max_value=int(datos['Cantidad de cuotas'].max()), value=(1, int(datos['Cantidad de cuotas'].max())))
    datos = datos[(datos['Cantidad de cuotas'] >= qtd_parcelas[0]) & (datos['Cantidad de cuotas'] <= qtd_parcelas[1])]



query  = """Producto in @Producto and\
            Precio >= @Precio[0] and Precio <= @Precio[1] and\
            `Fecha de Compra` >= @fecha_inicio and `Fecha de Compra` <= @fecha_fin and\
            `Categoría del Producto` in @categoria and\
            `Costo de envío` >= @frete[0] and `Costo de envío` <= @frete[1] and\
            `Método de pago` in @tipo_pagamento and\
            `Cantidad de cuotas` >= @qtd_parcelas[0] and `Cantidad de cuotas` <= @qtd_parcelas[1]
"""
datos_filtrados = datos.query(query)

with st.expander("Ver Datos Brutos"): 
    columnas = st.multiselect('Seleccione las Columnas a Mostrar', list(datos_filtrados.columns),list(datos_filtrados.columns))
    if columnas:
        datos_filtrados = datos_filtrados[columnas]
st.dataframe(datos_filtrados, height=200, use_container_width=True)

st.markdown(f" Total de Registros :blue[{datos_filtrados.shape[0]}] filas y {datos_filtrados.shape[1]} columnas")

st.markdown("##### Escribe un nombre para el archivo CSV :file_folder:")   
col1, col2 = st.columns(2)

with col1:
    nombre_archivo = st.text_input(" ",label_visibility="collapsed", value="datos_")
    nombre_archivo+=".csv"

with col2:
    st.download_button("Descargar CSV", convierte_csv(datos_filtrados), 
                    file_name=nombre_archivo,mime='text/csv', on_click=mensaje_exito)
