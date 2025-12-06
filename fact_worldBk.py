import pandas as pd

# Charger les tables
df_world = pd.read_csv("merged_athwld.csv")   # ton dataset ci-dessus
dim_country = pd.read_csv("dim_country.csv")
dim_date = pd.read_csv("dim_date.csv")

# Merge pour ajouter id_country
df_fact = df_world.merge(dim_country[['id_country', 'NOC']], on='NOC', how='left')

# Merge pour ajouter id_date
df_fact = df_fact.merge(dim_date[['id_date', 'Year']], on='Year', how='left')

# Garder seulement clés + mesures
fact_world = df_fact[
    [
        "id_country", "id_date",
        "nbr_partic_femmes", "nbr_partic_hommes",
        "per_Pop15_64", "per_Crois_PIB", "per_Taux_ActivFemmes",
        "per_pop_femmes", "per_pop_urbaine",
        "PIB", "Population Totale"
    ]
]

# Sauvegarder
fact_world.to_csv("fact_world.csv", index=False)


