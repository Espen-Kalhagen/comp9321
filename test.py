import pandas as pd
import numpy as np

vgs_csv_file = 'Video_Games_Sales_as_at_22_Dec_2016.csv'
vgs_df = pd.read_csv(vgs_csv_file)

gdp_csv_file = 'GDP.csv'
gdp_df = pd.read_csv(gdp_csv_file)

def clean_vgs_df():
    global vgs_df
    vgs_df = vgs_df[np.isfinite(vgs_df['Year_of_Release'])]

    vgs_df['Year_of_Release'] = vgs_df['Year_of_Release'].apply(
        lambda x: int(x) if not pd.isna(x) else np.nan)

clean_vgs_df()

print(vgs_df.loc[1].to_dict())

# year = '1999'
# country = "USA"

# gdp_df = gdp_df.set_index('Country Code')
# GDP = gdp_df.at[country,str(year)]

# vgs_df = vgs_df.groupby('Year_of_Release').sum()

# VG_Sales = vgs_df.at[int(year), 'NA_Sales']
# # groupby_year_df = groupby_year_df[["Global_Sales", "Critic_Score"]]

# # print(vgs_df)
# print(GDP)
# print(VG_Sales*1000000)
# print((VG_Sales*1000000)/GDP*100)
