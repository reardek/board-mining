import imp
from bs4 import BeautifulSoup
import mechanicalsoup
from odmantic import AIOEngine
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from database.models.board_game import BggDetails, BoardGameLinks
from database import engine

options = Options()
options.headless = True
driver_chrome = webdriver.Chrome("/usr/local/bin/chromedriver", options=options)

mechanical_browser = mechanicalsoup.Browser(soup_config={"features": "lxml"})


class BoardGameScrapper:
    game_name: str

    def __init__(self, game_name: str):
        self.game_name = game_name

    def get_links(self):
        rebel = self._find_link_rebel()
        if rebel:
            three_trolls = self._find_link_3trolle()
            bez_pradu = self._find_link_gry_bez_pradu()

            if three_trolls and bez_pradu:
                links = BoardGameLinks(
                    rebel=rebel, three_trolls=three_trolls, bez_pradu=bez_pradu
                )
                return links

    def _getHTMLdocument(self, url: str):
        response = requests.get(url)
        return response.text

    def _find_link_rebel(self):
        base_url = "https://www.rebel.pl"
        page = mechanical_browser.get(base_url)
        page.raise_for_status()
        search = mechanicalsoup.Form(page.soup.select_one(".form-search"))  # type: ignore
        search.input({"phrase": self.game_name})

        search_result = mechanical_browser.submit(search, page.url)
        driver_chrome.get(search_result.url)

        products_soup = BeautifulSoup(driver_chrome.page_source, "html.parser")
        product_links = products_soup.find_all("div", attrs={"class": "product"})
        for link in product_links:
            game_link = base_url + str(link.get("data-url"))
            driver_chrome.get(game_link)
            product_html = driver_chrome.page_source
            is_extension = (
                product_html.find("Uwaga! To nie jest samodzielna gra!") != -1 or product_html.find("Insert do gry") != -1
            )
            if not is_extension:
                return game_link

    def _find_link_3trolle(self):
        base_url = "https://3trolle.pl"
        page = mechanical_browser.get(base_url)
        page.raise_for_status()

        search = mechanicalsoup.Form(page.soup.select_one("#searchbox"))  # type: ignore
        search.input({"search_query": self.game_name})

        search_result = mechanical_browser.submit(search, page.url)
        driver_chrome.get(search_result.url)

        products_soup = BeautifulSoup(driver_chrome.page_source, "html.parser")
        product_links = products_soup.find_all("a", attrs={"class": "product_img_link"})

        for link in product_links:
            href = str(link.get("href"))
            driver_chrome.get(href)
            product_html = driver_chrome.page_source
            is_extension = (
                product_html.find("Uwaga! To nie jest samodzielna gra!") != -1
            )
            if not is_extension:
                return href

    def _find_link_gry_bez_pradu(self):
        base_url = "https://grybezpradu.eu"

        page = mechanical_browser.get(base_url)

        page.raise_for_status()

        search = mechanicalsoup.Form(page.soup.select_one(".search-form"))  # type: ignore

        search.input({"search": self.game_name})

        search_result = mechanical_browser.submit(search, page.url)

        products_page = self._getHTMLdocument(search_result.url)

        products_soup = BeautifulSoup(products_page, "html.parser")

        for link in products_soup.find_all("a", attrs={"class": "prodimage"}):
            game_link = base_url + str(link.get("href"))

            driver_chrome.get(game_link)
            html = driver_chrome.page_source
            product_soup = BeautifulSoup(html, "html.parser")
            description = product_soup.find("div", {"data-tab": "box_description"})
            if description:
                description_text = description.get_text().lower()
                is_extention_words = ["dodatek", "rozszerzenie", "insert"]
                isExtention = any(
                    [
                        description_text.find(rf"{extension_word}") != -1
                        or game_link.find(rf"{extension_word}") != -1
                        for extension_word in is_extention_words
                    ]
                )
                if not isExtention:
                    return game_link

    def _get_bgg_link(self, rebel_link: str):
        html = requests.get(rebel_link)
        product_page = BeautifulSoup(html.text, "html.parser")
        bgg_tag = product_page.find(
            "a", text="Opis w serwisie Board Game Geek", href=True
        )
        bgg_link: str = bgg_tag["href"]  # type: ignore

        bgg_link = "https:" + bgg_link
        redirect = requests.get(bgg_link)
        if redirect:
            return redirect.url

    def _get_bgg_description(self, bgg_page: BeautifulSoup):
        bgg_description = bgg_page.find("article", {"class": "game-description-body"})
        if bgg_description:
            return bgg_description

    def _get_bgg_title(self, bgg_description):
        bgg_title = bgg_description.find("strong")
        if bgg_title:
            return bgg_title  # type: ignore

    def _get_bgg_image(self, bgg_page: BeautifulSoup):
        bgg_image = bgg_page.find(
            "a", {"ng-show": "geekitemctrl.geekitem.data.item.imagepagehref"}
        )
        if bgg_image:
            bgg_image_link = bgg_image.find("img")
            if bgg_image_link:
                return bgg_image_link["ng-src"]  # type: ignore

    def get_info(self, rebel_link: str):
        bgg_link = self._get_bgg_link(rebel_link)
        driver_chrome.get(bgg_link)
        bgg_page = BeautifulSoup(driver_chrome.page_source, "html.parser")

        bgg_description = self._get_bgg_description(bgg_page)
        bgg_title = self._get_bgg_title(bgg_description)

        bgg_image = self._get_bgg_image(bgg_page)

        if bgg_link and bgg_description and bgg_title and bgg_image:
            game = BggDetails(
                title=bgg_title.get_text(),  # type: ignore
                description=bgg_description.get_text(),
                image=bgg_image, # type: ignore
                bgg_link=bgg_link,
            )
            return game

class BoardGamePriceScrapper:
    engine: AIOEngine

    def __init__(self, engine: AIOEngine):
        self.engine = engine

    