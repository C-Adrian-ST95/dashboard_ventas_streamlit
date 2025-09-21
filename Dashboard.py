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
    return f"{prefijo}{valor:.2f} mill"

st.set_page_config(layout="wide")

st.set_page_config(
    page_title="Carlos Adrian - Analista de Datos",
    page_icon="📊",
    layout="centered",
    menu_items={
        'Get Help': 'https://www.extendsclass.com/python-tester.html',
        'Report a Bug': 'https://github.com/C-Adrian-ST95/Dashboard_Ventas_Streamlit',
        'About': 'This is a simple dashboard for visualizing sales data.'
    }
)

st.title("Dashboard de Ventas :sunglasses:")

#url = "https://www.football-data.co.uk/spainm.php"
url = "https://ahcamachod.github.io/productos"

response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")
datos = pd.read_json(soup.pre.contents[0])
datos['Fecha de Compra'] = pd.to_datetime(datos['Fecha de Compra'], format='%d/%m/%Y')  


## filtradon por region y por año 

regiones_dict = {'Bogotá':'Andina', 'Medellín':'Andina', 'Cali':'Pacífica', 
                'Pereira':'Andina','Barranquilla':'Caribe', 'Cartagena':'Caribe',
                'Cúcuta':'Andina', 'Bucaramanga':'Andina', 'Riohacha':'Caribe', 
                'Santa Marta':'Caribe', 'Leticia':'Amazónica', 'Pasto':'Andina',
                'Manizales':'Andina', 'Neiva':'Andina', 'Villavicencio':'Orinoquía',
                'Armenia':'Andina', 'Soacha':'Andina','Valledupar':'Caribe', 'Inírida':'Amazónica'}

datos['Región'] = datos['Lugar de Compra'].map(regiones_dict)
datos['Año'] = datos['Fecha de Compra'].dt.year 

## sidebar para la interacción con la API

regiones = ['Colombia','Andina', 'Pacífica', 'Caribe', 'Amazónica', 'Orinoquía']
st.sidebar.title('Filtros')
region = st.sidebar.selectbox('Seleccione la Región', regiones)
if region == 'Colombia':
    datos = datos.loc[datos['Región'] != 'Colombia']
else:
    datos = datos.loc[datos['Región'] == region]

todos_anos = st.sidebar.checkbox('Datos de Todos el Periodo', value=True)

if not todos_anos:
    anio = st.sidebar.slider('Seleccione el Año', min_value=datos['Año'].min(), max_value=datos['Año'].max(), value=datos['Año'].max())
    datos = datos.loc[datos['Año'] == anio]

## Vendedores filtros
filtros_vendedores = st.sidebar.multiselect('Seleccione los Vendedores', datos['Vendedor'].unique())
if filtros_vendedores:      
    datos = datos[datos['Vendedor'].isin(filtros_vendedores)] 

## creación de features
fact_ciudades = datos.groupby('Lugar de Compra')[['Precio']].sum() # Agrupación de datos por ciudad


fact_ciudades = datos.drop_duplicates(subset=['Lugar de Compra'])[['Lugar de Compra','lat','lon']].merge(fact_ciudades, left_on='Lugar de Compra',right_index=True).sort_values('Precio', ascending=False)


facturacion_mensual = datos.set_index('Fecha de Compra').groupby(pd.Grouper(freq='ME'))['Precio'].sum().reset_index()

facturacion_mensual['Año'] = facturacion_mensual['Fecha de Compra'].dt.year
facturacion_mensual['Mes'] = facturacion_mensual['Fecha de Compra'].dt.month_name('es')

facturacion_cat = datos.groupby('Categoría del Producto')[['Precio']].sum().sort_values('Precio', ascending=False)

## creación de graficos 
fig_fact = px.scatter_geo(fact_ciudades, lat='lat', lon='lon', scope='south america'
                            ,size='Precio', template='seaborn', hover_name='Lugar de Compra',
                            hover_data={'lat':False, 'lon':False}, 
                            title='Facturación por Ciudad') 
fig_fact.update_geos(fitbounds="locations")

fig_facturacion_mensual = px.line(facturacion_mensual, x='Mes', y='Precio', markers=True,range_y=(0, facturacion_mensual.max()), title='Facturación Mensual',line_dash='Año', color='Año')
fig_facturacion_mensual.update_layout(yaxis_title='Facturación (COP)')


fig_facturacion_ciudades = px.bar(fact_ciudades.head(), x='Lugar de Compra', y = 'Precio', text_auto=True, title='Top Ciudades por Facturación')   
fig_facturacion_ciudades.update_layout(yaxis_title='Facturación')

fig_facturacion_cat = px.bar(facturacion_cat, text_auto=True, title='Facturación por Categoría')
fig_facturacion_cat.update_layout(yaxis_title='Facturación')

#st.metric('Cantidad de Ventas', cantidad_ventas['Categoría del Producto'].count(), border=True)

tab1, tab2, tab3 = st.tabs(["Facturación", "Cantidad de Ventas", "Vendedores"])

with tab1:

    col1, col2 = st.columns(2)

    with col1:
        st.metric('Facturación', formato_numero(datos['Precio'].sum(),'COP '), border=True)
        st.plotly_chart(fig_fact, use_container_width=True)
        st.plotly_chart(fig_facturacion_ciudades, use_container_width=True)
    with col2:
        st.metric('Cantidad de Ventas', formato_numero(datos.shape[0]), border=True)
        st.plotly_chart(fig_facturacion_mensual, use_container_width=True)
        st.plotly_chart(fig_facturacion_cat, use_container_width=True)


#### 2. Agrupación por categoría    

## agrupación por categoría
cantidad_ventas = datos.groupby('Categoría del Producto')[['Categoría del Producto']].count()
cantidad_ventas.rename(columns={
    "Categoría del Producto": "Cantidad de Productos"
}, inplace=True)
cantidad_ventas.index.name = "Categoría del Producto"

## cantidad_ventas_mensual
cantidad_ventas_mensual = datos.set_index('Fecha de Compra').groupby(pd.Grouper(freq='ME')).count().reset_index()
cantidad_ventas_mensual['Año'] = cantidad_ventas_mensual['Fecha de Compra'].dt.year
cantidad_ventas_mensual['Mes'] = cantidad_ventas_mensual['Fecha de Compra'].dt.month_name('es')

## cantidad_ventas_ciudades
cantidad_ventas_ciudades = datos.groupby('Lugar de Compra')[['Lugar de Compra']].count()

cantidad_ventas_ciudades = datos.drop_duplicates(subset=['Lugar de Compra'])[['Lugar de Compra','lat','lon']].merge(cantidad_ventas_ciudades, left_on='Lugar de Compra',right_index=True)
cantidad_ventas_ciudades = cantidad_ventas_ciudades[['Lugar de Compra','lat','lon','Lugar de Compra_y']].rename(columns={'Lugar de Compra_y': 'Cantidad de Ventas'}).sort_values('Cantidad de Ventas', ascending=False)
st.dataframe(cantidad_ventas_ciudades, height=200, use_container_width=True)

## cantidad_ventas_ciudades


# figuras ventas
fig_cantidad_ventas = px.bar(cantidad_ventas.sort_values('Cantidad de Productos', ascending=False), text_auto=True, title='Cantidad de Ventas por Categoría')
fig_cantidad_ventas.update_layout(yaxis_title='Cantidad de Ventas')

##  figura cantidad_ventas_mensual  
fig_cantidad_ventas_mensual = px.line(cantidad_ventas_mensual, x='Mes', y='Categoría del Producto', markers=True,range_y=(0, cantidad_ventas_mensual.max()), title='Cantidad de Ventas Mensual',line_dash='Año', color='Año')
fig_cantidad_ventas_mensual.update_layout(yaxis_title='Cantidad de Ventas')

## fig cantidad_ventas_ciudades 
fig_cantidad_ventas_ciudades = px.scatter_geo(cantidad_ventas_ciudades, lat='lat', lon='lon', scope='south america'
                            ,size='Cantidad de Ventas', template='seaborn', hover_name='Lugar de Compra',
                            hover_data={'lat':False, 'lon':False}, 
                            title='Facturación por Ciudad') 
fig_cantidad_ventas_ciudades.update_geos(fitbounds="locations")

## fig cantidad_ventas_ciudades barra
fig_ventas_ciudades = px.bar(cantidad_ventas_ciudades.head(), x='Lugar de Compra', y = 'Cantidad de Ventas', text_auto=True, title='Top Ciudades por Ventas')   
fig_ventas_ciudades.update_layout(yaxis_title='Cantidad de Ventas')

with tab2:
    
    col1, col2 = st.columns(2) 
    
    with col1:
        st.metric('Top Ciudad Venta', formato_numero(cantidad_ventas_ciudades['Cantidad de Ventas'].head(1).sum(),f'{cantidad_ventas_ciudades.iloc[0,0]} '), border=True)
        st.plotly_chart(fig_cantidad_ventas_ciudades, use_container_width=True)
        st.plotly_chart(fig_ventas_ciudades, use_container_width=True)

    with col2:
        st.metric('Cantidad de Ventas', formato_numero(cantidad_ventas['Cantidad de Productos'].sort_values(ascending=False).head(1).sum(),f'{cantidad_ventas['Cantidad de Productos'].sort_values(ascending=False).head(1).index[0]} '), border=True)


        st.plotly_chart(fig_cantidad_ventas_mensual, use_container_width=True)
        st.plotly_chart(fig_cantidad_ventas, use_container_width=True)
    st.dataframe(cantidad_ventas['Cantidad de Productos'].sort_values(ascending=False), height=200, use_container_width=True)
    
### 3er tab Vendedores  
vendedores = pd.DataFrame(datos.groupby('Vendedor')['Precio'].agg(['sum','count']))
vendedores.rename(columns={
    "sum": "Facturación (COP)",
    "count": "Cantidad de Ventas"
}, inplace=True)
vendedores = vendedores.sort_values('Facturación (COP)', ascending=False)


with tab3:
    ct_vendedores = st.number_input('Cantidad de Vendedores', 2,10,2)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric('Facturación', formato_numero(vendedores['Facturación (COP)'].sum(),'COP '), border=True)
        fig_facturacion_vendedores = px.bar(vendedores[["Facturación (COP)"]].sort_values('Facturación (COP)', ascending=False).head(ct_vendedores),x='Facturación (COP)', y=vendedores[['Facturación (COP)']].sort_values('Facturación (COP)', ascending=False).head(ct_vendedores).index, text_auto=True, title=f'top{ct_vendedores} Vendedores (Facturación)')
        fig_facturacion_vendedores.update_layout(yaxis_title="")
        st.plotly_chart(fig_facturacion_vendedores, use_container_width=True)
        
    with col2:
        st.metric('Cantidad de Ventas', formato_numero(vendedores['Cantidad de Ventas'].sum()), border=True)
        fig_cantidad_ventas_v = px.bar(vendedores[['Cantidad de Ventas']].sort_values('Cantidad de Ventas', ascending=False).head(ct_vendedores),x='Cantidad de Ventas', y=vendedores[['Cantidad de Ventas']].sort_values('Cantidad de Ventas', ascending=False).head(ct_vendedores).index, text_auto=True, title=f'top{ct_vendedores} Vendedores (Cantidad de Ventas)')
        fig_cantidad_ventas_v.update_layout(yaxis_title="")      
        st.plotly_chart(fig_cantidad_ventas_v, use_container_width=True)

    st.dataframe(vendedores, height=200, use_container_width=True)
    

    