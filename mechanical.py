from pydoc import classname
from bs4 import BeautifulSoup
import mechanicalsoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.headless = True
driver_chrome = webdriver.Chrome('/usr/local/bin/chromedriver', options=options)

mechanical_browser = mechanicalsoup.Browser(soup_config={"features": "lxml"})


def getHTMLdocument(url):
    response = requests.get(url)
    return response.text

def find_link_rebel(game_name: str):
    base_url = 'https://www.rebel.pl'
    page = mechanical_browser.get(base_url)
    page.raise_for_status()
    search = mechanicalsoup.Form(page.soup.select_one(".form-search"))
    search.input({"phrase": game_name})
    
    search_result = mechanical_browser.submit(search, page.url)
    driver_chrome.get(search_result.url)

    products_soup = BeautifulSoup(driver_chrome.page_source, "html.parser")
    product_links = products_soup.find_all("div", attrs={"class": "product"})
    for link in product_links:
        game_link = base_url + str(link.get("data-url"))
        driver_chrome.get(game_link)
        product_html = driver_chrome.page_source
        is_extension = product_html.find('Uwaga! To nie jest samodzielna gra!') == -1
        if is_extension:
            return game_link
            
def find_link_3trolle(game_name: str):
    base_url = 'https://3trolle.pl'
    page = mechanical_browser.get(base_url)
    page.raise_for_status()
    
    search = mechanicalsoup.Form(page.soup.select_one("#searchbox"))
    search.input({"search_query": game_name})
    
    search_result = mechanical_browser.submit(search, page.url)
    driver_chrome.get(search_result.url)
    
    products_soup = BeautifulSoup(driver_chrome.page_source, "html.parser")
    product_links = products_soup.find_all("a", attrs={"class": "product_img_link"})
    
    for link in product_links:
        href = str(link.get("href"))
        driver_chrome.get(href)
        product_html = driver_chrome.page_source
        is_extension = product_html.find('Uwaga! To nie jest samodzielna gra!') == -1
        if is_extension:
            return href


def find_link_gry_bez_pradu(game_name: str):
    base_url = "https://grybezpradu.eu"

    page = mechanical_browser.get(base_url)

    page.raise_for_status()
    #ignore
    search = mechanicalsoup.Form(page.soup.select_one(".search-form"))

    search.input({"search": game_name})

    search_result = mechanical_browser.submit(search, page.url)

    products_page = getHTMLdocument(search_result.url)

    products_soup = BeautifulSoup(products_page, "html.parser")

    for link in products_soup.find_all("a", attrs={"class": "prodimage"}):
        game_link = base_url + str(link.get("href"))

        driver_chrome.get(game_link)
        html = driver_chrome.page_source
        product_soup = BeautifulSoup(html, "html.parser")
        description = product_soup.find('div', {"data-tab": 'box_description'})
        if description:
            description_text = description.get_text().lower()
            is_extention_words = ['dodatek', 'rozszerzenie']
            isExtention = any([description_text.find(rf'{extension_word}') != -1 or game_link.find(rf'{extension_word}') != -1 for extension_word in is_extention_words])
            if not isExtention:
                return game_link