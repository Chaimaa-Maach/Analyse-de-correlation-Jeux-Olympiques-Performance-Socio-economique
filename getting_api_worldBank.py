import requests
import pandas as pd

# Indicateurs à récupérer + noms lisibles
indicators = {
    "SP.POP.1564.TO.ZS": "Population 15-64 ans (%)",
    "NY.GDP.MKTP.KD.ZG": "Croissance PIB (%)",
    "SL.TLF.CACT.FE.ZS": "Taux Activité Femmes (%)",
    "SP.POP.TOTL.FE.ZS": "Population Femmes (%)",
    "SP.URB.TOTL.IN.ZS": "Population Urbaine (%)",
    "NY.GDP.MKTP.CD": "GDP (USD)",
    "SP.POP.TOTL": "Population Totale"
}


# Fonction pour récupérer les données d'un indicateur
def get_indicator_data(indicator_code, start_year=1896, end_year=2022):
    url = (
        f"http://api.worldbank.org/v2/country/all/indicator/{indicator_code}"
        f"?date={start_year}:{end_year}&format=json&per_page=20000"
    )
    response = requests.get(url)
    data = response.json()

    if len(data) < 2 or not data[1]:
        print(f"Aucune donnée pour l'indicateur {indicator_code}")
        return pd.DataFrame()

    records = data[1]

    df = pd.json_normalize(records)
    df = df[['country.id', 'country.value', 'date', 'value']]
    df.columns = ['ISO3Code', 'Country Name', 'Year', indicator_code]
    df['Year'] = df['Year'].astype(int)



    return df


# Récupération et fusion des indicateurs
dfs = []
for code in indicators.keys():
    df = get_indicator_data(code, start_year=1896, end_year=2022)
    if not df.empty:
        dfs.append(df)

if dfs:
    merged_df = dfs[0]
    for df in dfs[1:]:
        merged_df = pd.merge(
            merged_df, df,
            on=['ISO3Code', 'Country Name', 'Year'],
            how='outer'
        )

    merged_df.rename(columns=indicators, inplace=True)
    merged_df.sort_values(by=['Country Name', 'Year'], inplace=True)

    print(merged_df.head())

else:
    merged_df = pd.DataFrame()
    print("Aucune donnée récupérée.")

# Export CSV
merged_df.to_csv("worldbank_indicators.csv", index=False)
