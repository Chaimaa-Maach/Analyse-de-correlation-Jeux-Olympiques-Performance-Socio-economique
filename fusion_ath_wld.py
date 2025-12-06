import pandas as pd

# Charger les fichiers
df_athl = pd.read_csv("merge_athl_reg_clean.csv")
df_wb = pd.read_csv("world_clean.csv")

print(df_athl.info())
# Vérifier le nombre de pays uniques
#nb_countries = df_athl['NOC'].nunique()
#print(f"Nombre de pays uniques dans athlètes : {nb_countries}")

# Créer deux DataFrames pour compter les participants par genre
df_femmes = df_athl[df_athl['Sex'] == 'F'].groupby(['NOC','Year','region'], as_index=False)['ID'].count()
df_femmes.rename(columns={'ID':'nbr_partic_femmes'}, inplace=True)

df_hommes = df_athl[df_athl['Sex'] == 'M'].groupby(['NOC','Year','region'], as_index=False)['ID'].count()
df_hommes.rename(columns={'ID':'nbr_partic_hommes'}, inplace=True)

# Fusionner les deux pour avoir une seule table par pays et année
df_athl_filt = pd.merge(df_femmes, df_hommes, on=['NOC','Year','region'], how='outer').fillna(0)

# Transformer les nombres en int
df_athl_filt['nbr_partic_femmes'] = df_athl_filt['nbr_partic_femmes'].astype(int)
df_athl_filt['nbr_partic_hommes'] = df_athl_filt['nbr_partic_hommes'].astype(int)

# Vérifier le résultat
print(df_athl_filt.head())

# Nombre de pays uniques dans la table filtrée
nb_countries_filt = df_athl_filt['NOC'].nunique()
print(f"Nombre de pays uniques dans df_athl_filt : {nb_countries_filt}")

# Filtrer WB pour ne garder que les pays et années présents dans df_athl_filt
df_wb_filtered = df_wb[
    df_wb['NOC'].isin(df_athl_filt['NOC'].unique()) &
    df_wb['Year'].isin(df_athl_filt['Year'].unique())
]

# Fusionner avec WB
df_merged = pd.merge(
    df_athl_filt,
    df_wb_filtered,
    on=['NOC','Year'],
    how='left'
)

df_merged.drop(columns=['region_y'], inplace=True)
df_merged.rename(columns={'region_x':'region'}, inplace=True)
# Sauvegarder
#df_merged.to_csv("merged_athwld.csv", index=False)
print(df_merged.head())
print(df_merged.info())