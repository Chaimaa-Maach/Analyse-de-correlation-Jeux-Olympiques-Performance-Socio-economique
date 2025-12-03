import pandas as pd


#Importation des fichiers csv dans des dataframes :
df_noc_reg = pd.read_csv("nocReg_clean.csv")
df_athl_even = pd.read_csv("athlEvent_clean.csv")



df_athl_even = df_athl_even.merge(df_noc_reg[['NOC', 'region']], on='NOC', how='left',suffixes=('', '_world'))
print(df_athl_even.info())
print(df_athl_even.head(20))

df_athl_even.loc[df_athl_even['NOC'] == 'SGP', 'region'] = 'Singapore'

df_athl_even.to_csv("merge_athl_reg_clean.csv", index=False)



"""verification
region_null = df_athl_even[df_athl_even['region'].isnull()].groupby('NOC').size()
print("nbr",region_null)"""


git add getting_api.py
git add data_cleaning.py
git add merge_files.csv

