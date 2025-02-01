import streamlit as st 
import pandas as pd
from app import df
from app import convert_csv
from app import mensagem_sucesso

st.title('Dataset de vendas')
with st.expander('Colunas'):
    colunas = st.multiselect(
        'Selecione as Colunas',
        list(df.columns),
        list(df.columns)
        )
st.sidebar.title('filtros') 
with st.sidebar.expander('Categoria do Produto'):
    categorias = st.multiselect(
        'Selecione as categorias',
        df['Categoria do Produto'].unique(),
        df['Categoria do Produto'].unique()
        ) 
with st.sidebar.expander('Preço do Produto'):
    preco_min, preco_max = st.slider(
        'Selecione o Preço',
        0, 5000,
        (0, 5000))
with st.sidebar.expander('Data da Compra'):
    data_inicio, data_fim = st.date_input(
        'Selecione a data',
        (df['Data da Compra'].min(), df['Data da Compra'].max())
    )

#query = '''
    #`Categoria do Produto` in @categorias and \
    #@preco <= Preço  <= @preco[1] and \
    #@data_compra[0] <= `Data da Compra` <= @data_compra[1]
#'''

data_inicio = pd.to_datetime(data_inicio)
data_fim = pd.to_datetime(data_fim)

filtro_dados = df[
    (df['Categoria do Produto'].isin(categorias)) &
    (df['Preço'] >= preco_min) & (df['Preço'] <= preco_max) &
    (df['Data da Compra'] >= data_inicio) & (df['Data da Compra'] <= data_fim)
]

filtro_dados = filtro_dados[colunas]
st.dataframe(filtro_dados)

st.markdown(f'A tabela possui :blue[{filtro_dados.shape[0]}] linhas e :blue[{filtro_dados.shape[1]}] colunas')

st.markdown('Escreva um nome do Arquivo')

coluna1, coluna2 = st.columns(2)
with coluna1:
    nome_arquivo = st.text_input(
        '',
        label_visibility='collapsed'
    )
    nome_arquivo += '.csv'
    
with coluna2:
    st.download_button(
        'Baixar arquivo',
        data=convert_csv(filtro_dados),
        file_name=nome_arquivo,
        mime='text/csv',
        on_click=mensagem_sucesso
    )
