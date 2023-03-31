
import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home",
    page_icon="Dado"
)

#image_path = r'C:\Users\Wanderley\Documents\repos\ftc_programacao_python\ciclo_6'

image = Image.open( 'logo.png' )
st.sidebar.image( image, width=120 )

st.sidebar.markdown( '# Cury Company' )
st.sidebar.markdown( '## Fastest Delivery in Town' )
st.sidebar.markdown( """___""" )

st.write( "# Curry Company Growth Dashboard" )

st.markdown(
    """
    Gowth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar esse Growth Dashboard?
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportameno.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Isights de geoloclização.
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento
    - Visão Restaurantes:
        - Indicadores semanais de crescimento dos restaurantes
    ### Ask for Help
    - Time de Data Science de Discord
        - @Wanderley
    """
)