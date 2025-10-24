import pandas as pd

#-------LIMPIEZA DE DATOS


#Importamos los archivos
df_monthly = pd.read_csv('./dat/monthly_stats.csv', delimiter="\t", encoding = 'UTF-16')
df_countries = pd.read_csv('./dat/country_iso.csv', encoding = 'UTF-8')
df_daily = pd.read_csv('./dat/daily_stats.csv', delimiter="\t", encoding = 'UTF-16')

#Empezados con monthly quitando las columnas que no necesitamos
df_month = df_monthly.drop(columns=['Unified Name', 'Unified ID', 'Unified Publisher Name', 'Unified Publisher ID', 'Publisher Name', 'Publisher ID', 'App Name', 'App ID'])
df_month = df_month.rename(columns={'Country / Region': 'Country_ISO', 'Revenue ($)' : 'Revenue', 'RPD ($)' : 'RPD'})

#Seguimos haciendo un merge con el df de países para añadir una columna con el nombre del pais según el codigo ISO
#Renombramos columnas y quitamos las que han mergeado que no necesitamos

# Aseguramos de que las columnas tengan el mismo formato
df_countries.columns = df_countries.columns.str.strip()
df_month.columns = df_month.columns.str.strip()

# Hacemos el merge entre ambos dataframes
df_month = df_month.merge(
    df_countries,
    how='left',  # left para conservar todos los datos de df_month
    left_on='Country_ISO',
    right_on='Code'
)

df_month = df_month.drop(columns=['Code'])
df_month = df_month.rename(columns={'Name': 'Country'})
# print(df_month)

#Hacemos lo mismo pero con daily stats

df_day = df_daily.drop(columns=['Unified Name', 'Unified ID', 'Unified Publisher Name', 'Unified Publisher ID', 'Publisher Name', 'Publisher ID', 'App Name', 'App ID'])
df_day = df_day.rename(columns={'Country / Region': 'Country_ISO', 'Revenue ($)' : 'Revenue', 'RPD ($)' : 'RPD', 'ARPDAU ($)' : 'ARPDAU'})

# Aseguramos de que las columnas tengan el mismo formato 
df_countries.columns = df_countries.columns.str.strip()
df_day.columns = df_day.columns.str.strip()

# Hacemos el merge entre ambos dataframes
df_day = df_day.merge(
    df_countries,
    how='left',  # left para conservar todos los datos de df_month
    left_on='Country_ISO',
    right_on='Code'
)

df_day = df_day.drop(columns=['Code'])
df_day = df_day.rename(columns={'Name': 'Country'})
print(df_day)

#Nos aseguramos que las fechas están en el formato correcto
df_month['Date'] = pd.to_datetime(df_month['Date'])
df_day['Date'] = pd.to_datetime(df_day['Date'])

#Generamos columnas adicionales Year, Month y Month name para facilitar la futura filtracion:
# Crear columnas adicionales para facilitar filtros
df_month['Year'] = df_month['Date'].dt.year
df_month['Month'] = df_month['Date'].dt.month
df_month['Month_Name'] = df_month['Date'].dt.strftime('%B')

df_day['Year'] = df_day['Date'].dt.year
df_day['Month'] = df_day['Date'].dt.month
df_day['Month_Name'] = df_day['Date'].dt.strftime('%B')


#DATOS LIMPIADOS; TENEMOS DOS DF DF_MONTH Y DF_DAY
df_month = df_month
df_day = df_day

