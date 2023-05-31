import pandas as pd
import streamlit as st
from azure.cosmos import exceptions, CosmosClient, PartitionKey
import json

## DATABASE
# conectarnos a la instancia
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

item_list_equipo = list(container_equipo.read_all_items())
item_list_pot_proy = list(container_potproy.read_all_items())
item_list_proy = list(container_proy.read_all_items())

lista_equipo = [item['equipo'] for item in item_list_equipo]

df_proyectos_equipo = pd.DataFrame(columns=['Tipo','Proyecto']+lista_equipo)
cont = 0
for item in item_list_proy:
    proyecto_id = item['id']
    if 'Run' in proyecto_id:
        tipo = 'Run'
    else:
        tipo = 'Pared'
    nombre = item['nombre']
    equipo = item['equipo']
    lista_participacion_proyecto = []
    for per in lista_equipo:
        if per in equipo:
            lista_participacion_proyecto.append(1)
        else:
            lista_participacion_proyecto.append(0)
    lista_temp = [tipo,nombre] + lista_participacion_proyecto
    df_proyectos_equipo.loc[cont] = lista_temp
    cont = cont + 1
    
for item in item_list_pot_proy:
    tipo = item['estado']
    nombre = item['nombre']
    equipo = item['equipo']
    lista_participacion_proyecto = []
    for per in lista_equipo:
        if per in equipo:
            lista_participacion_proyecto.append(1)
        else:
            lista_participacion_proyecto.append(0)
    lista_temp = [tipo,nombre] + lista_participacion_proyecto
    df_proyectos_equipo.loc[cont] = lista_temp
    cont = cont + 1

options_equipo = st.multiselect(
    '¿Que personas del equipo quieres ver?',
    lista_equipo,
    lista_equipo)

options_proyectos = st.multiselect(
    '¿Que tipo de proyectos quieres ver?',
    ['Pared', 'Run', 'Idea', 'Estimar'],
    ['Pared', 'Run', 'Idea', 'Estimar'])

df_proyectos_equipo = df_proyectos_equipo[df_proyectos_equipo['Tipo'].isin(options_proyectos)][['Tipo','Proyecto']+options_equipo]


st.dataframe(df_proyectos_equipo)