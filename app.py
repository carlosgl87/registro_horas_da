import pandas as pd
import streamlit as st
from azure.cosmos import exceptions, CosmosClient, PartitionKey
import json

######################################################################
## CSS to inject contained in a string
hide_table_row_index = """
            <style>
            thead tr th:first-child {display:none}
            tbody th {display:none}
            </style>
            """
st.markdown(hide_table_row_index, unsafe_allow_html=True)
######################################################################

######################################################################
## DATABASE
endpoint = "https://registrohoras.documents.azure.com:443/"
key = 'i4Jsp0MGQdqQY4QQvhJKM7SIJ2856GrzPmycWQjJOgEWDS93o8zjLwA1neNtGXkcaRyLc2PbdXGfACDbb06FEg=='
client = CosmosClient(endpoint, key)
DATABASE_NAME = 'controlhoras'
CONTAINER_NAME_PROYECTOS = 'Proyectos'
CONTAINER_NAME_POTENCIALESPROYECTOS = 'PotencialesProyectos'
CONTAINER_NAME_HORAS = 'RegistroHoras'
CONTAINER_EQUIPO = 'Equipo'

database = client.get_database_client(DATABASE_NAME)
container_proy = database.get_container_client(CONTAINER_NAME_PROYECTOS)
container_potproy = database.get_container_client(CONTAINER_NAME_POTENCIALESPROYECTOS)
container_horas = database.get_container_client(CONTAINER_NAME_HORAS)
container_equipo = database.get_container_client(CONTAINER_EQUIPO)
######################################################################

######################################################################
## Cargar los datos del equipo y crear la lista de campañas
item_list_equipo = list(container_equipo.read_all_items())
df_equipo = pd.DataFrame(columns=['id','equipo','puesto','tipo_equipo','estado'])
cont = 0
for item in item_list_equipo:
    df_equipo.loc[cont] = [item['id'],item['equipo'],item['puesto'],item['tipo_equipo'],item['estado']]
    cont = cont + 1
#df_equipo = pd.read_csv('data/equipo.csv',delimiter=';')
personas = list(df_equipo['equipo'].unique())
campanas = ['C4','C5','C6','C7','C8','C9','C10','C11','C12','C13']
######################################################################

######################################################################
## Elegir la persona y la campaña
col1, col2 = st.columns(2)
with col1:
   persona = st.selectbox(
    'Elegir Persona',
    personas)

with col2:
   campana = st.selectbox(
    'Elegir Campaña',
    campanas)
item_list_horas = list(container_horas.read_all_items())
item_list_proyectos = list(container_proy.read_all_items())
lista_proyectos_persona = [item['nombre'] for item in item_list_proyectos if persona in item['equipo']]
lista_proyectos_horas = [item for item in item_list_horas if item['equipo'] == persona and item['campana']==campana]

## Crear el dataframe para completar
df_horas_real = pd.DataFrame(columns = ['Proyecto','S1','S2','S3','S4'])
cont = 0
for proy in lista_proyectos_persona:
    lista_horas_bd = [item for item in lista_proyectos_horas if item['nombre'] == proy]
    if len(lista_horas_bd) == 0:
        lista_temp = [proy] + [0,0,0,0]
    else:
        lista_temp = [proy] + [item for item in lista_proyectos_horas if item['nombre'] == proy][0]['horas_campana']
    df_horas_real.loc[cont] = lista_temp
    cont = cont + 1
output_df_horas_real = st.experimental_data_editor(df_horas_real)

## Crear el proceso para registrar las horas reales en la base de datos
submit_button_pared = st.button("Registrar Horas Pared")
if submit_button_pared:
    for index, row in output_df_horas_real.iterrows():
        dictionario_horas = {
            'id':persona+'-'+row['Proyecto']+'-'+campana,
            'equipo':persona,
            'nombre':row['Proyecto'],
            'campana':campana,
            'horas_campana':[str(row['S1']),str(row['S2']),str(row['S3']),str(row['S4'])]}
        container_horas.upsert_item(dictionario_horas)
    st.success('Se actualizó correctamente las horas de proyectos de pared', icon="✅")

## Lo mismo pero para los proyectos para estimar
st.write('Proyectos para Estimar')

item_list_pot_proy = list(container_potproy.read_all_items())
lista_proyectos_estimar = [item for item in item_list_pot_proy if persona in item['equipo'] and item['estado'] == 'Estimar']

df_horas_real_estimar = pd.DataFrame(columns = ['Proyecto','S1','S2','S3','S4'])
cont = 0
for proy in lista_proyectos_estimar:
    lista_horas_bd = [item for item in lista_proyectos_horas if item['nombre'] == proy['nombre']]
    if len(lista_horas_bd) == 0:
        lista_temp = [proy['nombre']] + [0,0,0,0]
    else:
        lista_temp = [proy['nombre']] + [item for item in lista_proyectos_horas if item['nombre'] == proy['nombre']][0]['horas_campana']
    df_horas_real_estimar.loc[cont] = lista_temp
    cont = cont + 1

output_df_horas_estimar = st.experimental_data_editor(df_horas_real_estimar)

submit_button_estimar = st.button("Registrar Horas Estimacion")
if submit_button_estimar:
    for index, row in output_df_horas_estimar.iterrows():
        dictionario_horas = {
            'id':persona+'-'+row['Proyecto']+'-'+campana,
            'equipo':persona,
            'nombre':row['Proyecto'],
            'campana':campana,
            'horas_campana':[str(row['S1']),str(row['S2']),str(row['S3']),str(row['S4'])]}
        container_horas.upsert_item(dictionario_horas)
    st.success('Se actualizó correctamente las horas de estimacion', icon="✅")