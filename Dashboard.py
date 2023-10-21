import streamlit as st
import pandas as pd 
import requests 
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(layout= 'wide')

def formata_numero(valor, prefixo = ''):
    for unidade in ['','mil']:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'

st.title('DASHBOARD DE VENDAS :shopping_trolley:')

url = 'https://labdados.com/produtos'
regioes = ['Brasil','Centro-Oeste','Nordeste','Norte','Sudeste','Sul']

st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Região',regioes)

if regiao =='Brasil':
    regiao = ''

todos_anos = st.sidebar.checkbox('Dados de todo o período', value= True)  
if todos_anos:
    ano = ''
else:
    ano = st.checkbox.slider('Ano', 2020, 2023)

query_string = {'regiao':regiao.lower(),'ano':ano}
response = requests.get(url,params=query_string)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format= '%d/%m/%Y')

filtro_vendedores = st.sidebar.multiselect('Vendedores',dados['Vendedor'].unique())
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]

## --------------Tabelas ---------------------- 

receita_estados = dados.groupby('Local da compra')[['Preço']].sum().head(5).sort_values('Preço', ascending= False)

vendas_estados = dados.groupby('Local da compra')[['Preço']].count().head(5).sort_values('Preço', ascending= False)
vendas_estados = vendas_estados.rename(columns={'Preço': 'Vendas'})

mapa_estados = dados.drop_duplicates(
        subset = 'Local da compra')[['Local da compra','lat','lon']].merge(receita_estados, left_on= 'Local da compra', right_index= True).sort_values('Preço', ascending= False)

mapa__vendas_estados = dados.drop_duplicates(
        subset = 'Local da compra')[['Local da compra','lat','lon']].merge(vendas_estados, left_on= 'Local da compra', right_index= True).sort_values('Vendas', ascending= False)

receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq= 'M'))['Preço'].sum().reset_index()

receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

vendas_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq= 'M'))['Preço'].count().reset_index()

vendas_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
vendas_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()
vendas_mensal = vendas_mensal.rename(columns= {'Preço': 'Vendas'})

receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending= False)

vendas_categorias = dados.groupby('Categoria do Produto')[['Preço']].count()
vendas_categorias = vendas_categorias.rename(columns= {'Preço': 'Vendas'})
vendas_categorias = vendas_categorias.sort_values('Vendas', ascending= False)

### Tabelas vendedores
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum','count']))


## -------------- Gráficos ------------------------

fig_mapa_receita = px.scatter_geo(
mapa_estados,
lat= 'lat',
lon='lon',
scope= 'south america',
size= 'Preço',
template= 'seaborn',
title= 'Receita por estado')

fig_mapa_receita.update_layout(yaxis_title= 'Receita')

fig_mapa_vendas = px.scatter_geo(
mapa__vendas_estados,
lat= 'lat',
lon='lon',
scope= 'south america',
size= 'Vendas',
template= 'seaborn',
title= 'Vendas por estado')

fig_mapa_vendas.update_layout(yaxis_title= 'Vendas')

fig_receita_mensal = px.line(receita_mensal,
                             x= 'Mes',
                             y= 'Preço',
                             markers= True,
                             range_y= (0,receita_mensal.max()), 
                             color= 'Ano',
                             line_dash= 'Ano',
                             title= 'Receita mensal')

fig_vendas_mensal = px.line(vendas_mensal,
                             x= 'Mes',
                             y= 'Vendas',
                             markers= True,
                             range_y= (0,receita_mensal.max()), 
                             color= 'Ano',
                             line_dash= 'Ano',
                             title= 'Vendas mensal')

fig_receita_estados = px.bar(receita_estados,
                             text_auto= True,
                             title= 'Top estados (receita)')

fig_receita_estados.update_layout(yaxis_title= 'Receita')

fig_vendas_estados = px.bar(vendas_estados,
                             text_auto= True,
                             title= 'Top estados (vendas)')

fig_vendas_estados.update_layout(yaxis_title= 'Vendas')

fig_receita_categorias = px.bar(receita_categorias,
                             text_auto= True,
                             title= 'Reita categorias')

fig_receita_categorias.update_layout(yaxis_title= 'Receita')

fig_vendas_categorias = px.bar(vendas_categorias,
                             text_auto= True,
                             title= 'Vendas categorias')

fig_vendas_categorias.update_layout(yaxis_title= 'Vendas')

## ----------Visualização no Streamlit ----------------

# Abas 

aba1, aba2, aba3 = st.tabs(['Receita','Quantidade de vendas','Vendedores'])   

# Colunas 

with aba1:
    col1, col2 = st.columns(2)
    with col1:
        st.metric('Receita',formata_numero(dados['Preço'].sum(),'R$'))
        st.plotly_chart(fig_mapa_receita, use_container_width= True)
        st.plotly_chart(fig_receita_estados, use_container_width= True)
    with col2:
        st.metric('Quantidade de Vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal,use_container_width= True)
        st.plotly_chart(fig_receita_categorias, use_container_width= True)
with aba2:
    col1, col2 = st.columns(2)
    with col1:
        st.metric('Receita',formata_numero(dados['Preço'].sum(),'R$'))
        st.plotly_chart(fig_mapa_vendas, use_container_width= True)
        st.plotly_chart(fig_vendas_estados, use_container_width= True)
    with col2:
        st.metric('Quantidade de Vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_vendas_mensal,use_container_width= True)
        st.plotly_chart(fig_vendas_categorias, use_container_width= True)
with aba3:
    qtd_vendedores = st.number_input('Quantidade de vendedores', 2, 10, 5)
    col1, col2 = st.columns(2)
    with col1:
        st.metric('Receita',formata_numero(dados['Preço'].sum(),'R$'))
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending= False).head(qtd_vendedores),
                                        x = 'sum',
                                        y = vendedores[['sum']].sort_values('sum', ascending= False).head(qtd_vendedores).index,
                                        text_auto= True,
                                        title= f'Top {qtd_vendedores} vendedores (receita)'
                                        )
        st.plotly_chart(fig_receita_vendedores)
    with col2:
        st.metric('Quantidade de Vendas', formata_numero(dados.shape[0]))
        fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending= False).head(qtd_vendedores),
                                        x = 'count',
                                        y = vendedores[['count']].sort_values('count', ascending= False).head(qtd_vendedores).index,
                                        text_auto= True,
                                        title= f'Top {qtd_vendedores} vendedores (quantidade de vendas)'
                                        )
        st.plotly_chart(fig_vendas_vendedores)


# st.dataframe(dados) 



