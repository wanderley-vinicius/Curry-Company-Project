
# Bibliotecas
import folium
import re
import plotly.express as px
import plotly.graph_objects as go
from haversine import haversine

# Bibliotecas necessárias
import pandas as pd
import streamlit as st
from PIL import Image

from streamlit_folium import folium_static

st.set_page_config( page_title='Visão Empresa', page_icon='Gráfico', layout='wide')

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Funções
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=

def country_maps( df1 ):
    """  
        Essa função faz uma maração de pontos em um mapa localizando cada cidade por tráfego

        Sequência de passos:
        1. Criação da várivael dataplot para criar o filtro de cada cidade por tráfego
        2. Criação da váriavel map_ para criar o mapa
        3. Criação do for para fazer a interação do dataplot no map_ para fazer a marção de pontos

        Input: Dataframe
        Output: Map   
    """
    # Localização central de cada cidade por tipo de tráfego
    data_plot = (df1.loc[:, ['City', 
                          'Road_traffic_density',
                          'Delivery_location_latitude',
                          'Delivery_location_longitude']]
                  .groupby( ['City', 'Road_traffic_density'])
                  .median()
                  .reset_index())

    # Desenhar o mapa
    map_ = folium.Map()
    for index, location_info in data_plot.iterrows():
        folium.Marker( 
                [location_info['Delivery_location_latitude'],
                location_info['Delivery_location_longitude']],
                popup=location_info[
                ['City', 'Road_traffic_density']] ).add_to( map_ )

    folium_static( map_, width=1024, height=600 )

    return None

def order_share_by_week( df1 ):
    """ 
        Essa função retorna um gráfico de linha filtrado por qtd de pedidos por entregador por semana
        
        Sequência de passos:
        1. Criação da variável df_aux1 para filtrar as entregas por semana
        2. Criação da variável df_aux2 para filtrar os entregadores únicos por semana
        3. Criação da variável df_aux para por efetuar o cálculo entre as váriaveis df_aux1 e df_aux2
        4. Criação da variável fig que retorna um grpafico de linha
        
        Input: Dataframe
        Output: Graphic Line
    """
    # Quantidade de pedidos por entregador por Semana
    df_aux1 = (df1.loc[:, ['ID', 'week_of_year']]
                  .groupby( 'week_of_year' )
                  .count()
                  .reset_index())
    df_aux2 = (df1.loc[:, ['Delivery_person_ID', 'week_of_year']]
                  .groupby( 'week_of_year')
                  .nunique()
                  .reset_index())
    df_aux = pd.merge( df_aux1, df_aux2, how='inner' )

    df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']

    # gráfico de linha
    fig = px.line( df_aux, x='week_of_year', y='order_by_delivery' )

    return fig      

def order_by_week( df1 ):
    """ 
        Essa função cálcula a qtd de pedidos por semana e retorna um gráfico em linha
        
        Sequência de passos:
        1. Criação da variável df_aux para filtrar as entrefas por semana
        2. Ciação da variável fig que retorna uma gráfico de linha
        
        Input: Dataframe
        Output: Graphic Line
    """
    # Quantidade de pedidos por semana
    df_aux = (df1.loc[:, ['ID', 'week_of_year']]
                 .groupby('week_of_year')
                 .count()
                 .reset_index())
    # Gráfico
    fig = px.line( df_aux, x='week_of_year', y='ID' )

    return fig
        
def traffic_order_city( df1 ):
    """ 
        Essa função retorna um gráfico de bolhas onde o filtro é pelo volume de pedidos, cidade e tráfego
        
        Sequência de passos:
        1. Crição da variável cols para filtrar as colunas do dataframe
        2. Criação da variável df_aux para filtrar as colunas City e Road_traffic_density
        3. Criação da variável fig que retorna um gráfico de bolhas
        
        Input: Dataframe
        Output: Graphic Scatter
    """
    # Comparação do volume de pedidos por cidade e tipo de tráfego
    cols = ['ID', 'City', 'Road_traffic_density']
    df_aux = (df1.loc[:, cols]
                 .groupby(['City', 'Road_traffic_density'])
                 .count()
                 .reset_index())

    # Gráfico de Pizza
    fig = px.scatter( df_aux, x='City', y='Road_traffic_density', size='ID', color='City' )

    return fig

def traffic_order_share( df1 ):
    """ 
        Essa função retorna um gráfico de pizza filtrando a porcentagem dos pedidos pelo tráfego
        
        Sequência de passos:
        1. Criação da variável df_aux para filtrar Road_traffic_density
        2. Criação da coluna entregas_perc no dataframe para armarzenar a porcentagem de df_aux
        3. Criação da variável fig que retorna um gráfico de pizza
        
        Input: Dataframe
        Output: Graphic Pie
    """
    # Distribuição dos pedidos por tipo de tráfego
    df_aux = (df1.loc[:, ['ID', 'Road_traffic_density']]
                 .groupby( 'Road_traffic_density' )
                 .count()
                 .reset_index())
    df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()

    # Gráfico de Pizza
    fig = px.pie( df_aux, values='entregas_perc', names='Road_traffic_density' )

    return fig

def order_metric( df1 ):
    """ 
    Essa função retorna um gráfico de barras filtrando a qtd de pedidos por dia
    
    Sequência de passos:
    1. Criação da variável cols para filtrar as colunas
    2. Criação da variãvel df_aux para filtrar Order_Date
    3. Criação da variável  fig que retorna um gráfico de pizza
    
    Input: Dataframe
    Output: Graphic Pie
    """
    # Quantidade de pedidos por dia
    cols = ['ID', 'Order_Date']
    df_aux = (df1.loc[:, cols]
                .groupby(['Order_Date'])
                .count()
                .reset_index())
    # Gráfico de linha
    fig = px.bar( df_aux, x='Order_Date', y='ID')

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

df = pd.read_csv( '..\dataset\train.csv' )

# =-=-=-=-=-=-=-=-=-==-=-=-=-=
# Limpando os dados
# =-=-=-=-=-=-=-=-=-==-=-=-=-=

df1 = clean_code( df )

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=
#     Barra Lateral
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=

st.header( 'Marketplace - Visão Cliente' )

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

tab1, tab2, tab3= st.tabs( ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        # Oder Metric
        fig = order_metric( df1 )
        st.markdown( '# Orders by Day' )
        st.plotly_chart(fig, use_container_with=True)
            
    col1, col2 = st.columns( 2 )
    with st.container():
        with col1:
            fig = traffic_order_share( df1 )
            st.header( 'Traffic Order Share' )
            st.plotly_chart( fig, use_container_with=True )
  
        with col2:
            fig = traffic_order_city( df1 )
            st.header( 'Traffic Order CIty' )
            st.plotly_chart( fig, container_with=True )

with tab2:
    with st.container():
        fig = order_by_week( df1 )
        st.markdown( "# Order by Week" )
        st.plotly_chart( fig, use_container_width=True )

    with st.container(): 
        fig = order_share_by_week( df1 )
        st.markdown( "# Order Share by Week" )
        st.plotly_chart( fig, use_container_width=True )
    
with tab3:
        st.markdown( '# Country Maps' )
        country_maps( df1 )
