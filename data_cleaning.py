import pandas as pd
import numpy as np

#Importation des fichiers csv dans des dataframes :
df_noc_reg = pd.read_csv("noc_regions.csv")
df_athl_even = pd.read_csv("athlete_events.csv")
df_world = pd.read_csv("worldbank_indic.csv")

# Phase de Nettoyage:

# fichier1 : worldBank :
#renommer les colonnes pour simplifier le merge
df_world = df_world.rename(columns={'ISO3Code': 'NOC'})
df_world = df_world.rename(columns={'Country Name': 'region'})
df_world = df_world.rename(columns={'Population 15-64 ans (%)': 'per_Pop15_64'})
df_world = df_world.rename(columns={'Croissance PIB (%)': 'per_Crois_PIB'})
df_world = df_world.rename(columns={'Taux Activité Femmes (%)': 'per_Taux_ActivFemmes'})
df_world = df_world.rename(columns={'Population Femmes (%)': 'per_pop_femmes'})
df_world = df_world.rename(columns={'Population Urbaine (%)': 'per_pop_urbaine'})
df_world = df_world.rename(columns={'GDP (USD)': 'PIB'})

"""Vérifier le nombre des country null :
null_rows = df_world[df_world['NOC'].isnull()] 
print(null_rows.shape[0])"""

df_world = df_world.dropna(subset=['NOC'])
print(df_world.info())

df_world['PIB'] = df_world['PIB'].fillna(df_world.groupby(['NOC'])['PIB'].transform('mean'))
print(df_world[['NOC', 'PIB']].head(10))

df_world['per_pop_urbaine'] = df_world['per_pop_urbaine'].fillna(df_world.groupby(['NOC'])['per_pop_urbaine'].transform('median'))
print(df_world[['NOC', 'per_pop_urbaine']].head(10))

df_world['Population Totale'] = df_world['Population Totale'].fillna(df_world.groupby(['NOC'])['Population Totale'].transform('median'))
print(df_world[['NOC', 'Population Totale']].head(10))

df_world['per_Taux_ActivFemmes'] = df_world['per_Taux_ActivFemmes'].fillna(df_world.groupby(['NOC'])['per_Taux_ActivFemmes'].transform('min'))
print(df_world[['NOC', 'per_Taux_ActivFemmes']].head(10))

print(df_world.info())



# fichier1 : noc_region :



#creer une df extraite du df_world dont les valeurs uniques:
df_world_unique = df_world[['NOC', 'region']].drop_duplicates(subset='NOC')
#merge des df:
df_noc_reg = df_noc_reg.merge(df_world_unique[['NOC', 'region']], on='NOC', how='left',suffixes=('', '_world'))
df_noc_reg['region'] = df_noc_reg['region'].fillna(df_noc_reg['region_world'])
#suppression de la colonne ajoutée après le merge
df_noc_reg = df_noc_reg.drop(columns=['region_world'])
"""Vérification :
print(df_noc_reg.head())
print(df_noc_reg.info())"""
#Suppression des lignes inutiles:
inv_noc= df_noc_reg["NOC"].isin(["UNK","ROT"])
df_noc_reg = df_noc_reg[~inv_noc]
print(df_noc_reg.info())
df_noc_reg = df_noc_reg.drop(columns=['notes'])

df_noc_reg.drop_duplicates(subset=['NOC','region'], inplace=True)
print(df_noc_reg.info())

# fichier2 : athlet :

#Remplir "medal" par "Aucune"
df_athl_even['Medal']=df_athl_even['Medal'].fillna("Aucune")

#Remplir "age" par la mediane regroupe par 'Sport', 'Event', 'Year'
df_athl_even['Age'] = df_athl_even['Age'].fillna(df_athl_even.groupby(['Sport', 'Event', 'Year'])['Age'].transform('median'))
#Remplir "age" par la mediane regroupe par 'Sport'
df_athl_even['Age'] = df_athl_even['Age'].fillna(df_athl_even.groupby(['Sport'])['Age'].transform('median'))
df_athl_even['Age'] = df_athl_even['Age'].astype(int)

#Vérification :
print(df_athl_even[['Sport', 'Event', 'Year', 'Age','Medal']].head(10))
print(df_athl_even['Age'].isna().sum())
print(df_athl_even.info())

df_athl_even = df_athl_even.drop(columns=['Height','Weight','Games'])
print(df_athl_even.info())
df_athl_even.drop_duplicates(subset=['ID','Sex','Name','Team','NOC','Season','City','Sport', 'Event', 'Year', 'Age','Medal'], inplace=True)
print(df_athl_even.info())

inv_noc_ath= df_athl_even["NOC"].isin(["UNK","ROT"])
df_athl_even = df_athl_even[~inv_noc_ath]
print(df_athl_even.info())




df_athl_even.to_csv("athlEvent_clean.csv", index=False)
df_noc_reg.to_csv("nocReg_clean.csv", index=False)
