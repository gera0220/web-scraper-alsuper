from bs4 import BeautifulSoup as bs
import pandas as pd
import time
import numpy as np
from datetime import date
import csv
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

if(os.path.exists('data/productos_alsuper.csv')):
    pass
else:
    with open('data/productos_alsuper.csv', 'w') as file:
        writer = csv.writer(file)
        data = ['fecha', 'producto', 'departamento', 'precio_hoy', 'precio_reg', 'cantidad', 'medida', 'url']
        writer.writerow(data)

start_time = time.time()

path_alsuper = 'https://alsuper.com'

driver_path = 'C:/chromedriver.exe'
brave_path = 'C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe'

brave_options = webdriver.ChromeOptions()
brave_options.binary_location = brave_path
brave_options.add_experimental_option(
    # this will disable image loading
    "prefs", {"profile.managed_default_content_settings.images": 2}
)

drvr = webdriver.Chrome(options=brave_options, service=Service(driver_path))
drvr.get(path_alsuper)

soup = bs(drvr.page_source, 'html.parser')

# Obtener enlaces a departamentos
enlaces = soup.findAll('a', attrs={'class': 'ng-star-inserted'})

enlaces_departamentos = [enlaces[departamento]['href'] for departamento in range(len(enlaces))]
enlaces_departamentos = [enlace for enlace in enlaces_departamentos if 'departamento' in enlace]

flag = drvr.find_element(By.XPATH, '/html/body/app-root/div/app-home-footer/footer')

for departamento in enlaces_departamentos:
    drvr.get(path_alsuper + departamento)
    flag = drvr.find_element(By.XPATH, '/html/body/app-root/div/app-home-footer/footer')
    height_old = 0
    n_element = 16
    print(f'Obteniendo datos de: {path_alsuper + departamento}')
    while True:
        flag.location_once_scrolled_into_view
        drvr.execute_script("window.scrollBy(0, -400);")
        height_new = drvr.execute_script("return document.body.scrollHeight;")
        element_to_wait = '/html/body/app-root/div/mat-sidenav-container/mat-sidenav-content/app-department/div/div/div[1]/div[5]/app-product-card[' + str(n_element) + ']'
        try:
            myElem = WebDriverWait(drvr, 5).until(EC.presence_of_element_located((By.XPATH, element_to_wait)))
        except TimeoutException:
            print("Tiempo excedido. Se reducirá el número de elemento buscado.")
            n_element -= 6

        if height_old >= height_new:
            break
        height_old = height_new
        n_element += 15
 
    # Parsing the HTML
    soup = bs(drvr.page_source, 'html.parser')

    # Obtener categoría, nombres, precios, medida, url

    categoria = soup.find('mat-label', attrs={'class': 'as-roboto-slab as-font-24 depart'})
    categoria = categoria.text.strip()

    nombres = soup.findAll('mat-label', attrs={'class': 'as-font as-font-blackish'})
    nombres = [nombre.text.strip() for nombre in nombres]

    precios = soup.findAll('div', attrs={'class': 'as-product-price as-pointer as-font'})
    precios = [precio.text.strip() for precio in precios]

    medida = soup.findAll('mat-label', attrs={'class': 'as-font-10 as-font-grey-7e ng-star-inserted'})
    medida = [cantidad.text for cantidad in medida]

    url_productos = [url['href'] for url in soup.find_all('a', attrs={'class':'ng-star-inserted'}, href = True)]
    url_productos = [url for url in url_productos if 'producto' in url]
    url_productos = list(map(lambda url: 'https://alsuper.com' + url, url_productos))
    
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
        precio_reg_it = precio_reg_it[0].split('/')[0]
        precio_hoy.append(precio_hoy_it)
        precio_reg.append(precio_reg_it)

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

    # Multiplicar categoria
    categoria = [categoria] * len(medida)

    # Creación dataframe
    dict_prods = {'fecha':fecha, 'producto':nombres, 'departamento':categoria, 'precio_hoy':precio_hoy, 'precio_reg':precio_reg, 'cantidad':cantidad, 'medida':medido_en, 'url':url_productos}

    df = pd.DataFrame(dict_prods)

    df.to_csv('data/productos_alsuper.csv', mode='a', header=False, index=False)

final_time = time.time()

print(f'Tiempo de ejecución: {final_time - start_time}')