import pandas as pd
import os

flag = False

try:
    df_full = pd.read_parquet('data/productos_alsuper.parquet')
    df_new = pd.read_csv('data/productos_alsuper.csv')

    df_full = pd.concat([df_full, df_new])

    df_full.to_parquet('data/productos_alsuper.parquet')

    flag = True
except:
    print('Algo salió mal.')
finally:
    if flag:
        os.remove('data/productos_alsuper.csv')