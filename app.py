import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

ruta = 'https://github.com/juliandariogiraldoocampo/temporal/raw/refs/heads/main/estado_zni.csv'
df = pd.read_csv(ruta)

df = df.dropna()

df['ENERGÍA ACTIVA'] = df['ENERGÍA ACTIVA'].str.replace(',' , '').astype(float).astype(int)
df['ENERGÍA REACTIVA'] = df['ENERGÍA REACTIVA'].str.replace(',' , '').astype(float).astype(int)
df['POTENCIA MÁXIMA'] = df['POTENCIA MÁXIMA'].str.replace(',' , '').astype(float)

lista_cambio = [['Á', 'A'],['É', 'E'],['Í', 'I'],['Ó', 'O'],['Ú', 'U']]

for i in range(5):
    df['MUNICIPIO'] = df['MUNICIPIO'].str.replace(lista_cambio[i][0],lista_cambio[i][1])
    df['DEPARTAMENTO'] = df['DEPARTAMENTO'].str.replace(lista_cambio[i][0],lista_cambio[i][1])

condicion = ~df['DEPARTAMENTO'].isin([
    'ARCHIPIELAGO DE SAN ANDRES',
    'ARCHIPIELAGO DE SAN ANDRES y PROVIDENCIA',
    'ARCHIPIELAGO DE SAN ANDRES, PROVIDENCIA Y SANTA CATALINA'
])

df_colombia_continental = df[condicion]

# df Colombia Continental
categoria = ['DEPARTAMENTO', 'MUNICIPIO']
cols = ['ENERGÍA ACTIVA', 'ENERGÍA REACTIVA', 'POTENCIA MÁXIMA']
informe = df_colombia_continental.groupby(categoria)[cols].sum().reset_index()

# Cálculo de Total por Departamento y Año de Energía Activa
df_pivote = df_colombia_continental.pivot_table(
    index = 'DEPARTAMENTO',
    columns = 'AÑO SERVICIO',
    values = ['ENERGÍA ACTIVA'],
    aggfunc = 'sum'
).reset_index()

# Agrupación Energía Activa Total por año
df_energia_total = df_colombia_continental.pivot_table(
    columns = 'AÑO SERVICIO',
    values = ['ENERGÍA ACTIVA'],
    aggfunc = 'sum'
).reset_index()

#df_energia_activa 

filas = df.shape[0]
columnas = df.shape[1]

# df agrupando por Departamento, Año de servicio

df_depto_annos = df_colombia_continental.groupby(['DEPARTAMENTO', 'AÑO SERVICIO'])['ENERGÍA ACTIVA'].sum().reset_index()
departamento = df_depto_annos['DEPARTAMENTO'].unique().tolist()

# Cálculo de totales y deltas
tot_ac_25 = df_energia_total[2025].to_list()[0]
tot_ac_24 = df_energia_total[2024].to_list()[0]
tot_ac_23 = df_energia_total[2023].to_list()[0]
tot_ac_22 = df_energia_total[2022].to_list()[0]
tot_ac_21 = df_energia_total[2021].to_list()[0]

delta_25 = (tot_ac_25 - tot_ac_24)/tot_ac_24*100
delta_24 = (tot_ac_24 - tot_ac_23)/tot_ac_23*100
delta_23 = (tot_ac_23 - tot_ac_22)/tot_ac_22*100
delta_22 = (tot_ac_22 - tot_ac_21)/tot_ac_21*100

############# Visualización
st.set_page_config(
    page_title='Zonas No Interconectadas',
    layout='wide',
    )

st.markdown(
    '''
    <style>
        .block-container {
        max-width: 1000px
        }
    ''',
    unsafe_allow_html=True
)
#st.header('Dashboard Zonas no Interconectadas')
#st.header('Análisis de Datos')
#st.subheader('Tamaño del conjunto de datos')

st.markdown('<a id="inicio"> </a><br><br>', unsafe_allow_html=True)
st.image('img/encabezado.png')


#################################################################
#                 TAMAÑO DEL CONJUNTO DE DATOS                  #
#################################################################
st.markdown('<a id="acerca-de"> </a><br><br>', unsafe_allow_html=True)
st.html('<b>Acerca del Conjunto de Datos</b>')
col1, col2 = st.columns([0.25, 0.75])
with col1:
    st.markdown(
        f'''
        <h3 style =
        'color: #6542F2;
        background: #DFCAF840;
        border: 2px solid #4E7F96;
        border-radius: 10px;
        margin: 20px;
        padding: 10px;
        text-align: center'>
        <center>Número de Filass<br>{filas}</center>
        </h3>
        ''',
        unsafe_allow_html=True
    )


    st.markdown(
        f'''
        <h3 style =
        'color: #6542F2;
        background: #DFCAF840;
        border: 2px solid #4E7F96;
        border-radius: 10px;
        margin: 20px;
        text-align: center'>
        <center>Número de Columnas<br>{columnas}</center>
        </h3>
        ''',
        unsafe_allow_html=True
    )
with col2:
    with st.expander('Ver conjunto de datos completo'):
        st.dataframe(df)
    with st.expander('Ver datos de Energía Activa por Departamento y Año'):
        st.dataframe(df_pivote)

#############################################################
# GRÁFICO INTERACTIVO DE BARRAS HORIZONTALES POR DEPTO Y AÑO #
#############################################################
st.markdown('<a id="evolucion"> </a><br><br>', unsafe_allow_html=True)

with st.container(border=True):
    st.html('<center><b>Evolución de Energía Activa por Departamento</b></center>')
    
    # Desplegable para seleccionar un departamento
    depto_select = st.selectbox(
        'Seleccione un departamento:',
        options = departamento
    )

    condicion_filtro = df_depto_annos['DEPARTAMENTO']==depto_select
    df_depto_desplegar = df_depto_annos[condicion_filtro]



    # Crear gráfico de barras horizontales
    # 1. Crear el objeto Figure
    fig_barras = go.Figure()

    # 2. Agregar barras a Figure
    fig_barras.add_trace(go.Bar(
        x=df_depto_desplegar['ENERGÍA ACTIVA'],
        y=df_depto_desplegar['AÑO SERVICIO'].astype(str),
        orientation='h',
        marker_color='#4E7F96',
        text=df_depto_desplegar['ENERGÍA ACTIVA'],
        texttemplate='%{text:,.0f}',
        textposition='auto'
        )
    )

    # 3. Actualizar el objeto Figure con el diseño deseado
    fig_barras.update_layout(
        height=400,
        xaxis_title='Energía Activa kWh',
        yaxis_title='Año de Servicio',
        showlegend=False,
        yaxis={'categoryorder':'category ascending'}
    )

    # Mostrar 
    st.plotly_chart(fig_barras,use_container_width=True)


#################################################################
#   INDICADORES DE ENERGÍA ACTIVA POR AÑO EN MILLONES DE kWh    #
#################################################################
st.markdown('<a id="indicadores"> </a><br><br>', unsafe_allow_html=True)
st.html('<b>Indicadores de Energía Activa por año en Millones de kWh</b>')

col3, col4, col5, col6 = st.columns(4)
col3.metric(
      label='2022',
      value=round((tot_ac_22/1000000),2),
      delta=f'{round(delta_22,2)}%',
      help='Energía Activa Total en 2022',
      border=True
)

col4.metric(
      label='2023',
      value=round(tot_ac_23/1000000,2),
      delta=f'{round(delta_23,2)}%',
      border=True
)

col5.metric(
      label='2024',
      value=round(tot_ac_24/1000000,2),
      delta=f'{round(delta_24,2)}%',
      border=True
)

col6.metric(
      label='2025',
      value=round(tot_ac_25/1000000,2),
      delta=f'{round(delta_25,2)}%',
      border=True
)

if st.checkbox('Mostrar detalles el Dataset'):
        st.write('Conjuto de datos obtendios del Portal de Datos Abiertos del Gobierno Nacional de Colombia')
        st.write('Disponible en https://www.datos.gov.co/Minas-y-Energ-a/Estado-de-la-prestaci-n-del-servicio-de-energ-a-en/3ebi-d83g/about_data')

with st.expander('Ver datos de Energía Activa por Dpto y Año:'):
    st.dataframe(df_pivote)


with st.container(border=True):
    df_energia_total = df_energia_total[[2022, 2023, 2024, 2025]].T


    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df_energia_total.index,
            y=df_energia_total[0],
            mode='lines+markers',
            line=dict(color="#4E7F96")
        )
    )
    st.title('Energía Activa Total por Año')
    st.plotly_chart(fig)
    st.caption('*Fuente Datos Abiertos Gobierno Nacional*')


#######################################################################
#     GRÁFICOS BARRAS ENERGÍA ACTIVA Y REACTIVA kWh POR MUNICIPIO     #
#######################################################################
st.markdown('<a id="barras"> </a><br><br>', unsafe_allow_html=True)

with st.container(border=True):
    st.html('<font size=5><font color=#3D6E85> Gráficos de Energía Activa y Reactiva por municipio</font>')
    col7, col8 = st.columns(2)

    with col7:
        # Del df agrupado (informe), ordenamos por Energía activa descendente y elegimos los 5 primeros
        df_mayores = informe.sort_values(by='ENERGÍA ACTIVA', ascending=False).head(5)
        #st.dataframe(df_mayores)
        
        # 1. Crear objeto y agregar gráficos
        fig = px.bar(
            df_mayores,
            x='MUNICIPIO',
            y='ENERGÍA ACTIVA',
            color='DEPARTAMENTO',
            title='Top 5 Municipios Energía Activa',
            labels={'MUNICIPIO': 'Municipios', 'ENERGÍA ACTIVA': 'Energía Activa (kWh)', 'DEPARTAMENTO':'Departamento'},
            color_discrete_sequence=px.colors.sequential.Tealgrn,
            height=500

        )

        # 2. Actualización del diseño
        fig.update_traces(
            textposition='outside',
            texttemplate='%{y:,.0f}'
        )

        # 3. Mostrar
        st.plotly_chart(fig, use_container_width=True)



    with col8:
    # Del df agrupado (informe), ordenamos por Energía activa descendente y elegimos los 5 primeros
        df_mayores = informe.sort_values(by='ENERGÍA REACTIVA', ascending=False).head(5)
        #st.dataframe(df_mayores)
    
        # 1. Crear objeto y agregar gráficos
        fig = px.bar(
            df_mayores,
            x='MUNICIPIO',
            y='ENERGÍA REACTIVA',
            color='DEPARTAMENTO',
            title='Top 5 Municipios Energía Reactiva',
            labels={'MUNICIPIO': 'Municipios', 'ENERGÍA REACTIVA': 'Energía Reactiva (kWh)', 'DEPARTAMENTO':'Departamento'},
            #color_discrete_sequence=px.colors.sequential.Tealgrn,
            height=500

        )

        # 2. Actualización del diseño
        fig.update_traces(
            textposition='outside',
            texttemplate='%{y:,.0f}'
        )

        # 3. Mostrar
        st.plotly_chart(fig, use_container_width=True)


#######################################################################
#   GRÁFICOS TORTAS ENERGÍA ACTIVA Y REACTIVA kWh POR DEPARTAMENTO    #
#######################################################################
st.markdown('<a id="tortas"> </a><br>', unsafe_allow_html=True)

with st.container(border=True):
    st.html('<font size=5><font color=#3D6E85> Gráficos de Energía Activa y Reactiva por municipio</font>')

    col9, col10 = st.columns(2)
    with col9:
        df_depto_activa = informe.groupby('DEPARTAMENTO')['ENERGÍA ACTIVA'].sum().reset_index()
        df_depto_activa = informe.sort_values(by='ENERGÍA ACTIVA', ascending=False).head(5)

        # 1. Crear objeto y agregar gráficos
        fig_act = px.pie(
            df_depto_activa,
            names='DEPARTAMENTO',
            values='ENERGÍA ACTIVA',
            title = 'Top 5 Departamentos - Energía Activa',
            hole=0.4
        )

        # 2. Actualización del diseño


        # 3. Mostrar
        st.plotly_chart(fig_act, use_container_width=True)

        with col10:
            df_depto_activa = informe.groupby('DEPARTAMENTO')['ENERGÍA REACTIVA'].sum().reset_index()
            df_depto_activa = informe.sort_values(by='ENERGÍA REACTIVA', ascending=False).head(5)

            # 1. Crear objeto y agregar gráficos
            fig_act = px.pie(
                df_depto_activa,
                names='DEPARTAMENTO',
                values='ENERGÍA REACTIVA',
                title = 'Top 5 Departamentos - Energía Reactiva',
                hole=0.4
            )

            # 2. Actualización del diseño


            # 3. Mostrar
            st.plotly_chart(fig_act, use_container_width=True)

#################################################################
#                     MENÚ EN BARRA LATERAL                     #
#################################################################

with st.sidebar.container():
    st.markdown('''
                <style>
                [data-testid="stSidebar"] a {
                diaplay: block;
                text-decoration: none;
                }
                <style>
                [data-testid="stSidebar"] a:hover {
                background-color: #FFFFFF;
                }
            ''',
            unsafe_allow_html=True)
    st.header('Menú de navegación')
    st.markdown('[Inicio](#inicio)')
    st.markdown('[Acerca de](#acerca-de)')
    st.markdown('[Evolución de Energía Activa](#evolucion)')
    st.markdown('[Indicadores de Energía Activa](#indicadores)')
    st.markdown('[Gráfico por Municipio](#barras)')
    st.markdown('[gráfico por Departamento](#tortas)')