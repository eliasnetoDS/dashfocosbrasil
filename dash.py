import pandas as pd
import geopandas as gpd
import folium
import streamlit as st
from streamlit_folium import folium_static
from datetime import datetime, timedelta

# Cria o dashboard
st.title('Focos de Calor no Brasil')
st.markdown('Este dashboard apresenta os focos de calor do dia de ontem. Você também pode selecionar datas anteriores, até 40 dias antes de hoje')


# Obter a data de ontem
yesterday = datetime.now() - timedelta(days=1)

# Adiciona um widget de data para permitir ao usuário selecionar a data desejada
selected_date = st.date_input('Selecione uma data', value = pd.to_datetime(yesterday))

# Formata a data no formato usado no link
date_str = selected_date.strftime('%Y%m%d')

# Lê os dados de focos de calor
csv_url = f'https://queimadas.dgi.inpe.br/home/downloadfile?path=%2Fapp%2Fapi%2Fdata%2Fdados_abertos%2Ffocos%2FDiario%2Ffocos_abertos_24h_{date_str}.csv'


# Filtra os dados do INPE com base na data selecionada pelo usuário
df = pd.read_csv(csv_url, delimiter=',')
df['data_hora_gmt'] = pd.to_datetime(df['data_hora_gmt']) # converter para datetimelike
df = df[df['data_hora_gmt'].dt.date == selected_date]


df = df.query("pais == 'Brasil'")

# Converte as coordenadas para o formato correto
df['latitude'] = df['lat']
df['longitude'] = df['lon']

# Cria um GeoDataFrame com as coordenadas
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude))

# Cria um mapa com os focos de calor
m = folium.Map(location=[-15.788497, -47.879873], zoom_start=4)

for idx, row in gdf.iterrows():
    # Adiciona um marcador com o nome da cidade e estado
    tooltip = f"{row['municipio']} - {row['estado']}"
    folium.Marker(location=[row['latitude'], row['longitude']], tooltip=tooltip, icon=folium.Icon(color='red')).add_to(m)

# Mostra o mapa
folium_static(m)


import plotly.express as px

# Agrupa os focos de calor por estado e conta o número de ocorrências
df_count = df.groupby('estado').size().reset_index(name='count')

# Ordena o DataFrame pela coluna 'count' em ordem decrescente
df_count = df_count.sort_values('count', ascending=False)


# Plota o gráfico de barras com os dados ordenados
fig = px.bar(df_count, x='estado', y='count', color='estado')

fig.update_layout(
    xaxis_title="Estados",
    yaxis_title="Número de focos de calor"
)

# Mostra o gráfico
st.plotly_chart(fig)