from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

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
    print(f'vieja: {height_old}')
    flag.location_once_scrolled_into_view
    drvr.execute_script("window.scrollBy(0, -400);")
    height_new = drvr.execute_script("return document.body.scrollHeight;")
    print(f'nueva: {height_new}')
    time.sleep(5)
    if height_old == height_new:
        break
    height_old = height_new

