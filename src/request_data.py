import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import time
import numpy as np
from datetime import date
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

start_time = time.time()

options = Options()
driver_path = '/home/gera0220/chromedriver'
brave_path = '/opt/brave.com/brave/brave'

options.binary_location = brave_path
options.add_argument('--remote-debugging-port=9224')

drvr = webdriver.Chrome(options=options, service=Service(driver_path))
drvr.get('https://alsuper.com/departamento/frutas-y-verduras-1')

flag = drvr.find_element(By.XPATH, '/html/body/app-root/div/app-home-footer/footer')
height_old = 0

while True:
    flag.location_once_scrolled_into_view
    drvr.execute_script("window.scrollBy(0, -400);")
    height_new = drvr.execute_script("return document.body.scrollHeight;")
    time.sleep(5)
    if height_old == height_new:
        break
    height_old = height_new

r = requests.get('https://alsuper.com/departamento/frutas-y-verduras-1')
 
# Parsing the HTML
soup = bs(drvr.page_source, 'html.parser')

# Obtener nombres, precios y medida
nombres = soup.findAll('mat-label', attrs={'class': 'as-font as-font-blackish'})
nombres = [nombre.text.strip() for nombre in nombres]

precios = soup.findAll('div', attrs={'class': 'as-product-price as-pointer as-font'})
precios = [precio.text.strip() for precio in precios]

medida = soup.findAll('mat-label', attrs={'class': 'as-font-10 as-font-grey-7e ng-star-inserted'})
medida = [cantidad.text for cantidad in medida]

# Dividir entre precios del día de hoy y los normales (misma variable)
precios = [precios.split(' ') for precios in precios]

# Si el precio de hoy y normal es el mismo duplica el precio de hoy
for i in precios:
    if len(i) == 1:
        i.append(i[0])

# Separa precios de hoy y regular en diferentes variables
precio_hoy = []
precio_reg = []
for i in range(len(precios)):
    precio_hoy_it, precio_reg_it = np.split(np.array(precios[i]), 2)
    precio_hoy_it = precio_hoy_it[0].split('/')[0]
    precio_hoy.append(precio_hoy_it)
    precio_reg.append(precio_reg_it[0])

# Separa la cantidad y el sistema en que se está midiendo (diferentes variables)
cantidad = []
medido_en = []
for i in range(len(medida)):
    if('KG' == medida[i]):
        medida[i] = medida[i].replace('KG', '1 KG')
    cantidad_it, medido_en_it = medida[i].split(' ')
    cantidad.append(cantidad_it)
    medido_en.append(medido_en_it)

# Fecha de consulta
fecha = date.today()
fecha = [fecha] * len(medida)

# Creación dataframe
dict_prods = {'fecha':fecha, 'producto':nombres, 'precio_hoy':precio_hoy, 'precio_reg':precio_reg, 'cantidad':cantidad, 'medida':medido_en}

df = pd.DataFrame(dict_prods)

pd.DataFrame.to_csv(pd.DataFrame(df), 'data/productos_alsuper_hoy.csv')

final_time = time.time()

print(f'Tiempo de ejecución: {final_time - start_time}')