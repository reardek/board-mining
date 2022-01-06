from pydoc import classname
from bs4 import BeautifulSoup
import mechanicalsoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re

options = Options()
options.headless = True
driverChrome = webdriver.Chrome('/usr/bin/chromedriver', options=options)

def getHTMLdocument(url):
    response = requests.get(url)
    return response.text


browser = mechanicalsoup.Browser(soup_config={"features": "lxml"})

base_url = "https://grybezpradu.eu"

page = browser.get(base_url)

page.raise_for_status()
#ignore
search = mechanicalsoup.Form(page.soup.select_one(".search-form"))

search.input({"search": "Terraformacja Marsa"})

search_result = browser.submit(search, page.url)

products_page = getHTMLdocument(search_result.url)

products_soup = BeautifulSoup(products_page, "html.parser")


try: 
    for link in products_soup.find_all("a", attrs={"class": "prodimage"}):
        isBaseGameLink = base_url + link.get("href")

        driverChrome.get(isBaseGameLink)
        html = driverChrome.page_source
        product_soup = BeautifulSoup(html, "html.parser")
        description = product_soup.find_all('div', {"itemprop": 'description'})[0].text
        isExtention = bool(re.findall(r'dodatek', description, re.IGNORECASE)) or bool(re.findall(r'rozszerzenie', description, re.IGNORECASE)) or bool(re.findall(r'dodatek', isBaseGameLink, re.IGNORECASE))
        print(f'{isBaseGameLink}: {isExtention}')
    product_link = base_url + products_soup.find_all("a", attrs={"class": "prodimage"})[0].get("href")
except IndexError:
    print("Nie znaleziono gry")