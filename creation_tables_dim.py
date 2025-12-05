import pandas as pd

df = pd.read_csv("merge_athl_reg_clean.csv")

print(df.info())

#table dim_athlete :

#Ajout de la colonne is_medalist :
df['Medal'] = df['Medal'].str.capitalize()
medals = ["Gold", "Silver", "Bronze"]
df['is_medalist'] = df['Medal'].apply(lambda x: x in medals)

#Ajout de la colonne nbr_medals :
df['nbr_medal'] = df['Medal'].apply(lambda x: 1 if x in medals else 0)

#Ajout de la colonne score_pondere :
score_map = {
    "Gold": 3,
    "Bronze": 1,
    "Silver": 2,
    "Aucune": 0
}
df['score_pondere'] = df['Medal'].map(score_map)

dim_athlete = df.groupby(
    ['ID', 'Name', 'Sex', 'Team', 'NOC', 'Sport'],
    as_index=False
).agg({
    'is_medalist': 'max',
    'nbr_medal': 'sum',
    'score_pondere': 'sum'
})

# Sauvegarde dans fichier csv :
dim_athlete.to_csv("dim_athlete.csv", index=False)

#table dim_medal :

# Liste des types de médailles :
medal_types = ["Gold", "Silver", "Bronze", "Aucune"]

# Construction de la table :
dim_medal = pd.DataFrame({
    "id_medal": range(1, len(medal_types) + 1),
    "type_medal": medal_types,
    "score_pondere": [score_map[m] for m in medal_types]
})

# Sauvegarde dans le fichier :
dim_medal.to_csv("dim_medal.csv", index=False)


#table dim_country :


dim_country = df[['NOC', 'region']].drop_duplicates().reset_index(drop=True)
dim_country['id_country'] = range(1, len(dim_country) + 1)
dim_country = dim_country[['id_country', 'NOC', 'region']]

# Sauvegarde dans le fichier :
dim_country.to_csv("dim_country.csv", index=False)

#table dim_event :

dim_event = df[['Event', 'Season','Year','NOC','Sport']].drop_duplicates(subset=['Event']).reset_index(drop=True)
dim_event['id_event'] = range(1, len(dim_event) + 1)
dim_event = dim_event[['id_event','Event', 'Season','Year','NOC','Sport']]


# Sauvegarde dans le fichier :
dim_event.to_csv("dim_event.csv", index=False)


#table dim_date :

df['Medal'] = df['Medal'].str.capitalize()

# Compter uniquement les vraies médailles
df['has_medal'] = df['Medal'].apply(lambda x: 1 if x in ["Gold","Silver","Bronze"] else 0)

# Calcul du nombre de médailles par année
nbr_med_per_year = df.groupby('Year', as_index=False)['has_medal'].sum()
nbr_med_per_year.rename(columns={'has_medal': 'nbr_med_per_year'}, inplace=True)

# Créer dim_date
dim_date = nbr_med_per_year.copy()

dim_date['id_date'] = range(1, len(dim_date) + 1)
dim_date = dim_date[['id_date','Year','nbr_med_per_year']]

# Sauvegarde dans le fichier :
dim_date.to_csv("dim_date.csv", index=False)



