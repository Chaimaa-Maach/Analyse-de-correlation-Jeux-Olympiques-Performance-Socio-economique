import pandas as pd

df = pd.read_csv("merge_athl_reg_clean.csv")
df1 = pd.read_csv("merged_athwld.csv")

print(df.info())

#table dim_athlete :

dim_athlete = df[['ID', 'Name', 'Sex']].drop_duplicates()
dim_athlete.rename(columns={'ID': 'id_athlete'}, inplace=True)
# Sauvegarde en CSV
dim_athlete.to_csv("dim_athlete.csv", index=False)


#table dim_medal :

# Liste des types de médailles :
medal_types = ["Gold", "Silver", "Bronze", "Aucune"]
score_map = {
    "Gold": 3,
    "Bronze": 1,
    "Silver": 2,
    "Aucune": 0
}
# Construction de la table :
dim_medal = pd.DataFrame({
    "id_medal": range(1, len(medal_types) + 1),
    "type_medal": medal_types,
    "score_pondere": [score_map[m] for m in medal_types]
})
# Sauvegarde dans le fichier :
dim_medal.to_csv("dim_medal.csv", index=False)


#table dim_country :


dim_country = df1[['NOC', 'region']].drop_duplicates().reset_index(drop=True)
dim_country['id_country'] = range(1, len(dim_country) + 1)
dim_country = dim_country[['id_country', 'NOC', 'region']]
# Sauvegarde dans le fichier :
dim_country.to_csv("dim_country.csv", index=False)

#table dim_event :

dim_event = df[['Event', 'Season','Sport']].drop_duplicates()
dim_event['id_event'] = range(1, len(dim_event) + 1)
dim_event = dim_event[['id_event','Event', 'Season','Sport']]
# Sauvegarde dans le fichier :
dim_event.to_csv("dim_event.csv", index=False)


#table dim_date :

dim_date = df[['Year']].drop_duplicates()
dim_date['id_date'] = range(1, len(dim_date) + 1)
dim_date = dim_date[['id_date','Year']]
# Sauvegarde dans le fichier :
dim_date.to_csv("dim_date.csv", index=False)


print(dim_country.info())
print(dim_event.info())
print(dim_date.info())
print(dim_medal.info())
print(dim_athlete.info())



