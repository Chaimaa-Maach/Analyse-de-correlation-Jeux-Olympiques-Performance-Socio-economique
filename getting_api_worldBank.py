import requests
import pandas as pd

#Liste des indicateurs et noms lisibles
indicators = {
    "NY.GDP.MKTP.CD": "GDP",  # PIB
    "SP.POP.TOTL": "Population",  # Population
    "EN.GHG.CO2.MT.CE.AR5": "CO2"  # Emissions CO2
}


#Fonction pour récupérer les données d'un indicateur
def get_indicator_data(indicator_code, start_year=1896, end_year=2022):
    url = f"http://api.worldbank.org/v2/country/all/indicator/{indicator_code}?date={start_year}:{end_year}&format=json&per_page=20000"
    response = requests.get(url)
    data = response.json()

    # Vérification si l'API renvoie des données
    if len(data) < 2 or not data[1]:
        print(f"Aucune donnée pour l'indicateur {indicator_code}")
        return pd.DataFrame()

    records = data[1]

    # Conversion en DataFrame
    df = pd.json_normalize(records)
    df = df[['country.id', 'country.value', 'date', 'value']]
    df.columns = ['ISO3Code', 'Country Name', 'Year', indicator_code]
    df['Year'] = df['Year'].astype(int)

    return df


#Récupération et fusion des indicateurs
dfs = []
for code in indicators.keys():
    df = get_indicator_data(code, start_year=1896, end_year=2022)
    if not df.empty:
        dfs.append(df)

# Merge successif pour avoir chaque indicateur comme colonne
if dfs:
    merged_df = dfs[0]
    for df in dfs[1:]:
        merged_df = pd.merge(merged_df, df, on=['ISO3Code', 'Country Name', 'Year'], how='outer')

    # Renommer les colonnes avec les noms lisibles
    merged_df.rename(columns=indicators, inplace=True)

    # Tri par pays et année
    merged_df.sort_values(by=['Country Name', 'Year'], inplace=True)

    # Affichage du résultat
    print(merged_df.head())
else:
    merged_df = pd.DataFrame()
    print("Aucune donnée récupérée.")
merged_df.to_csv("worldbank_indicators.csv", index=False)

git config --global user.name "Chaimaa Maach"
git config --global user.email "maachechaimaa@gmail.com"
