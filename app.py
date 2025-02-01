import json
import pandas as pd
import streamlit as st
import plotly.express as px
import time 

# Carregue o arquivo JSON
file = open('vendas.json')
data = json.load(file)

# Crie o DataFrame a partir dos dados
df = pd.DataFrame.from_dict(data)

# Converta a coluna 'Data da Compra' para o formato datetime
df['Data da Compra'] = pd.to_datetime(
    df['Data da Compra'],
    errors='coerce',  # Lida com valores inválidos
    dayfirst=True     # Garante que o dia vem antes do mês
)

# Função para formatar valores monetários
def format_number(value, prefix=''):
    for unit in ['', 'mil']:
        if value < 1000:
            return f'{prefix} {value:.2f} {unit}'
        value /= 1000
        
    return f'{prefix} {value:.2f} milhões'

# 1 - Dataframe receita estado
df_rec_estado = df.groupby('Local da compra')[['Preço']].sum()
df_rec_estado = df.drop_duplicates(subset='Local da compra')[['Local da compra', 'lat', 'lon']].merge(df_rec_estado, left_on='Local da compra', right_index=True).sort_values('Preço', ascending=False)

# 2 - Dataframe Receita mensal
df_rec_mensal = df.set_index('Data da Compra').groupby(pd.Grouper(freq='ME'))['Preço'].sum().reset_index()
df_rec_mensal['Ano'] = df_rec_mensal['Data da Compra'].dt.year
df_rec_mensal['Mes'] = df_rec_mensal['Data da Compra'].dt.month_name()

# Dataframe receita por categoria
df_rec_categoria = df.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)

# DataFrame vendedores
df_vendedores = pd.DataFrame(df.groupby('Vendedor')['Preço'].agg(['sum', 'count']))

# Função para converter arquivo csv 
@st.cache_data
def convert_csv(df):
    return df.to_csv(index=False).encode('utf-8')

def mensagem_sucesso():
    success = st.success(
        'Arquivo baixado com sucesso',
        icon="download.png"
        )
    time.sleep(3)
    success.empty()
# Criação dos gráficos
grafico_map_estado = px.scatter_geo(
    df_rec_estado,
    lat='lat',
    lon='lon',
    scope='south america',
    size='Preço',
    template='seaborn',
    hover_name='Local da compra',
    hover_data={'lat': False, 'lon': False},
    title='Receita por Estado',
)

grafico_rec_mensal = px.line(
    df_rec_mensal,
    x='Mes',
    y='Preço',
    markers=True,
    range_y=(0, df_rec_mensal['Preço'].max()),
    color='Ano',
    title='Receita Mensal',
)
grafico_rec_mensal.update_layout(yaxis_title='Receita')

grafico_rec_estado = px.bar(
    df_rec_estado.head(7),
    x='Local da compra',
    y='Preço',
    text_auto=True,
    title='Top Receita por Estados',
)

grafico_rec_categoria = px.bar(
    df_rec_categoria.head(7),
    text_auto=True,
    title='Top 7 Categorias com Maior Receita',
)

grafico_rec_vendedores = px.bar(
    df_vendedores[['sum']].sort_values('sum', ascending=False).head(7),
    x = 'sum',
    y = df_vendedores[['sum']].sort_values('sum', ascending=False).head(7).index,
    text_auto= True,
    title= 'Top 7 Vendedores por Receita'
)

grafico_vendas_vendedores = px.bar(
    df_vendedores[['count']].sort_values('count', ascending=False).head(7),
    x = 'count',
    y = df_vendedores[['count']].sort_values('count', ascending=False).head(7).index,
    text_auto= True,
    title= 'Top 7 vendedores por vendas ',
)
# Configuração do Streamlit
st.set_page_config(layout='wide')
st.title("Dashboard de Vendas :shopping_trolley:")

# Filtros do Dshboard
st.sidebar.title('Filtro de Vendedores')

filtro_vendedor = st.sidebar.multiselect(
    'Vendedores',
    df['Vendedor'].unique(),
    
)

if filtro_vendedor:
    df = df[df['Vendedor'].isin(filtro_vendedor)]
# Criação das abas no Streamlit
aba1, aba2, aba3 = st.tabs(['Dataset', 'Receita', 'Vendedores'])

# Aba 1 - Mostrar o dataset
with aba1:
    st.dataframe(df)

# Aba 2 - Exibir gráficos de receita
with aba2:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita Total', format_number(df['Preço'].sum(), 'R$'))
        st.plotly_chart(grafico_map_estado, use_container_width=True)
        st.plotly_chart(grafico_rec_estado, use_container_width=True)
    with coluna2:
        st.metric('Quantidade de vendas', format_number(df.shape[0]))
        st.plotly_chart(grafico_rec_mensal, use_container_width=True)
        st.plotly_chart(grafico_rec_categoria, use_container_width=True)
    with aba3:
        coluna1, coluna2 = st.columns(2)
        with coluna1:
            st.plotly_chart(grafico_rec_vendedores)
        with coluna2:
            st.plotly_chart(grafico_vendas_vendedores)
# Feche o arquivo JSON após o uso
file.close()
