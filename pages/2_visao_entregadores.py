
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

st.set_page_config( page_title='VIsão Entregadores', page_icon='Entregadores', layout='wide')

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Funções
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=

def top_delivers( df1, top_asc ):
    df2 = (df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
              .groupby(['City', 'Delivery_person_ID'])
              .mean()
              .sort_values( ['City', 'Time_taken(min)'], ascending=top_asc).reset_index())

    df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)

    df3 = pd.concat( [df_aux01, df_aux02, df_aux03] ).reset_index(  drop=True )

    return df3

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

st.header( 'Marketplace - Visão Entregadores' )

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

st.header( date_slider )
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

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '', ''] )

with tab1:
    with st.container():
        st.title('Overall Matrics')
        
        col1, col2, col3, col4 = st.columns( 4, gap='large' )
        with col1:
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric( 'Maior idade', maior_idade )
            
        with col2:
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric( 'Menor idade', menor_idade )
        
        with col3:
            melhor_condicao = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric( 'Melhor condição de veículo', melhor_condicao )
            
        with col4:
            pior_condicao = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric( 'Pior condição de veículo', pior_condicao )
            
    with st.container():
        st.markdown( """---""" )
        st.title( 'Avaliações' )
        
        col1, col2 = st.columns( 2 )
        with col1:
            st.markdown( '##### Avaliação médias por Enregador' )
            df_avg_ratings__per_delivery = (df1.loc[:, ['Delivery_person_ID', 'Delivery_person_Ratings']]
                                                     .groupby(['Delivery_person_ID'])
                                                     .mean()
                                                     .reset_index())
            st.dataframe( df_avg_ratings__per_delivery )
            
        with col2:
            st.markdown( '##### Avaliação média por trâsito' )
            avaliacao_por_trafego = (df1.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']]
                                        .groupby('Road_traffic_density')
                                        .agg({ 'Delivery_person_Ratings': ['mean', 'std'] }))
            # mudança do nome das colunas
            avaliacao_por_trafego.columns = ['delivery_mean', 'delivery_std']
            # resetando o index
            avaliacao_por_trafego = avaliacao_por_trafego.reset_index()
            st.dataframe( avaliacao_por_trafego )

            
            st.markdown( '##### Avaliação média por clima' )
            avg_por_clima = ( df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']]
                                 .groupby('Weatherconditions')
                                 .agg({ 'Delivery_person_Ratings': ['mean', 'std'] }))

            # troca nome das colunas
            avg_por_clima.columns = ['delivery_mean', 'delivery_std']
            # reseta o index
            avg_por_clima.reset_index()
            st.dataframe( avg_por_clima )

    with st.container():
        st.markdown( """---""" )
        st.title( 'Velocidade de Entregas' )
        
        col1, col2 = st.columns( 2 )
        
        with col1:
            st.markdown( '##### Top Entregadores mais rápidos' )
            df3 = top_delivers( df1, top_asc=True )
            st.dataframe( df3 )
            
        with col2:
            st.markdown( '##### Top Entregadores mais lentos' )
            f3 = top_delivers( df1, top_asc=False )
            st.dataframe( df3 )
            
        
            