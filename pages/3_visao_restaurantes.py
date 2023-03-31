
# Bibliotecas
import folium
import re
import plotly.express as px
import plotly.graph_objects as go
from haversine import haversine

# Bibliotecas necessárias
import pandas as pd
import numpy as np
import streamlit as st
from PIL import Image

from streamlit_folium import folium_static

st.set_page_config( page_title='VIsão Restaurantes', page_icon='Restaurante', layout='wide')


# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Funções
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=

# O tempo médio e o desvio padrão de entrega por cidade e tipo de tráfego.
def avg_std_time_on_traffic( df1 ):
    cols = ['Time_taken(min)', 'City', 'Road_traffic_density']
    df_aux = (df1.loc[:, cols]
                 .groupby(['City', 'Road_traffic_density'])
                 .agg( { 'Time_taken(min)': ['mean', 'std'] } ))

    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    # Gráfico de pizza
    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
                      color='std_time', color_continuous_scale='RdBu',
                      color_continuous_midpoint=np.average(df_aux['std_time']))
    return fig

def avg_std_time_graph( df1 ):
                # O tempo médio e o desvio padrão de entrega por cidade.
                df_aux = (df1.loc[:, ['Time_taken(min)', 'City']]
                             .groupby('City')
                             .agg( { 'Time_taken(min)': ['mean', 'std'] } ))
                df_aux.columns = ['avg_time', 'std_time']
                df_aux = df_aux.reset_index()

                # Gráfico de barras com desvio padrão
                fig = go.Figure()
                fig.add_trace( go.Bar( name='Control', 
                                        x=df_aux['City'],
                                        y=df_aux['avg_time'], 
                                        error_y=dict(type='data', 
                                        array=df_aux['std_time']) ) )
                fig = fig.update_layout(barmode='group')

                return fig

def avg_std_time_delivery(df1, festival, op):
    """
        Essa função calcula o tempo médio e o desvio padrão do tempo de entrega.
        Parâmetros:
        Input:
            - df: Dataframe com os dados necessário para o cálculo
            - op: Tipo de operações que precisa ser calculado
                'avg_time': Calcula o tempo médio
                'std_time': Calcula o desvio padrão do tempo
        Output:
            - df: Dataframe com 2 colunas e 1 lina
    """

    df_aux = (df1.loc[:, ['Time_taken(min)', 'Festival']]
                 .groupby('Festival')
                 .agg( {'Time_taken(min)': ['mean', 'std']} ))

    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    linhas_selecionadas = df_aux['Festival'] == festival
    df_aux = np.round( df_aux.loc[linhas_selecionadas, 'avg_time'], 2)
    
    return df_aux

def distance( df1, fig ): 
    if fig == False:
        # Distância média das entregas
        cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 
                'Restaurant_latitude', 'Restaurant_longitude']
        df1['distance'] = df1.loc[:, cols].apply( lambda x: 
                            haversine( 
                                (x['Restaurant_latitude'], x['Restaurant_longitude']), 
                                (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1 )
        avg_distance = np.round( df1['distance'].mean(), 2 )

        return avg_distance
    else:
        # Tempo médio de entrega por cidade
        cols = ['Delivery_location_latitude', 'Delivery_location_longitude',
                'Restaurant_latitude', 'Restaurant_longitude']
        df1['distance'] = df1.loc[:, cols].apply( lambda x: 
                        haversine( 
                            (x['Restaurant_latitude'], x['Restaurant_longitude']), 
                            (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1 )
        # Calculo da média
        avg_distance = df1.loc[:, ['City', 'distance']].groupby( 'City' ).mean().reset_index()
        fig = go.Figure( data=[ go.Pie( labels=avg_distance['City'], 
                                        values=avg_distance['distance'], 
                                        pull=[0, 0.1, 0] ) ] )
        return fig
        
            
def clean_code( df1 ):
    """
        Esta função tem a responsabilidade de limpar o dataframe
        
        Tipos de limpeza
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Reoção dos espaços das variáveis de texo
        4. Formatação da coluna de datas
        5. Lipeza da coluna de tempo ( remoção do texto da variável numérica )
        
        Input: Dataframe
        Output: Dataframe     
    """
    
    # 1. Convertendo a coluna Age de texto para número
    linhas_selecionadas = df1['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()

    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int )

    # 2. Convertendo a coluna Ratings de texto para número decimal (float) 
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype( float )

    # 3. Convertendo a coluna order_date de texto para data
    df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format='%d-%m-%Y')

    # 4. Convertendo multiple_deliveries de texto para numero inteiro 9( int )
    linhas_selecionadas = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )

    # Removendo linhas NaN
    linhas_selecionadas = df1['Road_traffic_density'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = df1['City'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()

    # inserindo a coluna semana no data frame
    df1['week_of_year'] = df1['Order_Date'].dt.strftime( '%U')

    # 5. Removendo os espaços deentro de strings/texto/object
    # df1 = df1.reset_index( drop=True )
    # for i in range( len( df1 )):
    #  df1.loc[i, 'ID'] = df1.loc[i, 'ID'].strip()

    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()
    
    # Limpando a coluna de time taken
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split( '(min)' )[1] )
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype( int )
    
    return df1

# _-_-_-_-_-_- Inicío da Estrutura lógica do código _-_-_-_-_-_-

# =-=-=-=-=-=-=-=-=-==-=-=-=-=
# Import dataset
# =-=-=-=-=-=-=-=-=-==-=-=-=-=

df = pd.read_csv( 'train.csv' )

# =-=-=-=-=-=-=-=-=-==-=-=-=-=
# Limpando os dados
# =-=-=-=-=-=-=-=-=-==-=-=-=-=

df1 = clean_code( df )

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=
#     Barra Lateral
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=

st.header( 'Marketplace - Visão Restaurantes' )

image_path = 'logo.png'
image = Image.open( image_path )
st.sidebar.image( image, width=120 )


st.sidebar.markdown( '# Cury Company' )
st.sidebar.markdown( '## Fastest Delivery in Town' )
st.sidebar.markdown( """___""" )

st.sidebar.markdown( '## Selecione uma data limite' )

date_slider = st.sidebar.slider(
        'Até qual valor?',
        value=pd.datetime( 2022, 4, 13 ),
        min_value=pd.datetime( 2022, 2, 11 ),
        max_value=pd.datetime( 2022, 4, 6 ),
        format='DD-MM-YYY')


st.sidebar.markdown( """___""" )

traffic_options = st.sidebar.multiselect(
        'Quais as condições do trânsito',
        ['Low', 'Medium', 'High', 'Jam'],
        default=['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown( """___""" )
st.sidebar.markdown( '### Powered by Comunidade DS' )

# Filtro Data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de traânsito
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas, :]

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=
#     Layout no Streamlit
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '_', '_'] )

with tab1:
    with st.container():
        col1, col2, col3, col4, col5, col6 = st.columns( 6 )
        with col1:
            # Entregadores únicos do dataframe
            delivery_person_uniques = len(df1.loc[:, 'Delivery_person_ID'].unique())
            col1.metric( 'Entregadores únicos', delivery_person_uniques )
             
        with col2:
            avg_distance = distance( df1, fig=False )
            col2.metric( 'A distância média das entregas', avg_distance )

        with col3:
            df_aux = avg_std_time_delivery( df1, 'Yes', 'avg_time' )
            col3.metric( 'Tempo médio de Entrega c/ Festival', df_aux )
            
        with col4:
            df_aux = avg_std_time_delivery( df1, 'Yes', 'std_time' )
            col4.metric( 'Desvio padrão médio de entrega c/ Festival', df_aux )

        with col5:
            df_aux = avg_std_time_delivery( df1, 'No', 'avg_time' )
            col5.metric( 'Tempo médio de Entrega c/ Festival', df_aux )
            
        with col6:
            df_aux = avg_std_time_delivery( df1, 'No', 'std_time' )
            col6.metric( 'Desvio padrão médio de entrega c/ Festival', df_aux )
        
    with st.container():
            # Tempo médio de entrega por cidade
            avg_distance = distance( df1, fig=True )
            st.plotly_chart( avg_distance )
    
    with st.container():
        col1, col2 = st.columns( 2 )
        
        with col1:
            fig = avg_std_time_graph( df1 )
            st.plotly_chart( fig )
            
        with col2:
            # O tempo médio e o desvio padrão de entrega por cidade e tipo de tráfego.
            fig = avg_std_time_on_traffic( df1 )
            st.plotly_chart( fig )

    with st.container():
        cols = ['Time_taken(min)', 'City', 'Type_of_order']
        df_aux = df1.loc[:, cols].groupby(['City', 'Type_of_order']).agg( { 'Time_taken(min)': ['mean', 'std'] } )

        df_aux.columns = ['avg_mean', 'avg_std']
        df_aux = df_aux.reset_index()
        
        st.dataframe( df_aux )
