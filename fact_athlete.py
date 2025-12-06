import pandas as pd

# Charger les tables
athl = pd.read_csv("merge_athl_reg_clean.csv")          #
dim_athlete = pd.read_csv("dim_athlete.csv")  # id_athlete, Name, Sex
dim_country = pd.read_csv("dim_country.csv")  # id_country, NOC, region
dim_event = pd.read_csv("dim_event.csv")      # id_event, Event, Sport, Season
dim_date = pd.read_csv("dim_date.csv")        # id_date, Year
dim_medal = pd.read_csv("dim_medal.csv")      # id_medal,type_medal,score_pondere
fact_worls = pd.read_csv("fact_world.csv")    # ids_dim_tables + is_medalist, nbr_medal, score_pondere




# Normaliser Medal
athl['Medal'] = athl['Medal'].str.capitalize()

# is_medalist : 1 si médaille, sinon 0
medals = ["Gold", "Silver", "Bronze"]
athl['is_medalist'] = athl['Medal'].apply(lambda x: 1 if x in medals else 0)

# score_pondere
score_map = {"Gold": 3, "Silver": 2, "Bronze": 1}
athl['score_pondere'] = athl['Medal'].map(score_map).fillna(0).astype(int)


# Ajouter ID Athlète
fact = athl.merge(dim_athlete[['id_athlete','Name','Sex']], left_on=['ID','Name','Sex'], right_on=['id_athlete','Name','Sex'],how='left')

# Ajouter ID pays
fact = fact.merge(dim_country[['id_country','NOC']], on='NOC', how='left')

# Ajouter ID événement
fact = fact.merge(dim_event[['id_event','Event','Sport','Season']], on=['Event','Sport','Season'], how='left')

# Ajouter ID date
fact = fact.merge(dim_date[['id_date','Year']], on='Year', how='left')

# Ajouter ID médaille
fact = fact.merge(dim_medal[['id_medal','type_medal']], left_on='Medal', right_on='type_medal', how='left')

# Sélectionner uniquement les clés et les mesures
fact_table = fact[['id_athlete','id_country','id_event','id_date','id_medal','is_medalist','score_pondere']]


# Sauvegarder
fact_table.to_csv("fact_athlete.csv", index=False)

print(fact_table.info())