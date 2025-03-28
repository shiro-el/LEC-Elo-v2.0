import pandas as pd
import dataframe_image as dfi

df = pd.read_csv("lec.csv", encoding="euc-kr")
df = df.iloc[::-1].reset_index(drop=True)

df = df.drop(columns=['상위 브라켓 진출'])

numeric_columns = df.select_dtypes(include=['float64']).columns
df[numeric_columns] = df[numeric_columns].round(2)

dfi.export(df, 'lec.jpg')