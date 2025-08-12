import os
import time
from urllib.parse import urljoin
from typing import List, Dict
import re

from base_scraper import BaseScraper

from custom_logger.custom_logger import ChatDota2Logger

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException


logger = ChatDota2Logger()


class ItemsScraper(BaseScraper):
    def __init__(self, **kwargs):

        super().__init__(**kwargs)
        self.dota_wiki_base_url = "https://liquipedia.net/dota2/"
        self.items_wiki_base_url = "https://liquipedia.net/dota2/Items"
        self.neutral_items_wiki_base_url = "https://liquipedia.net/Neutral_Items"

        self.main_page_elem = None
        self.main_elem_children = None
        # TODO: main_elem_children_processed to be removed
        self.main_elem_children_processed = None
        self.items_titles = None


    def accept_cookies(self) -> None:
        """
        Accepts the cookies that are needed to browse the dota wiki
        :return:
        """
        try:
            # Locate the "Accept" button using its data attribute
            accept_button = self.browser.find_element(
                By.XPATH,
                "//button[contains(text(), 'Accept')]"
            )

            # Click the "Accept All" button
            accept_button.click()
            logger.info("Clicked the 'Accept' button successfully.")

        except NoSuchElementException:
            logger.info("Accept button not found!")

    def browse_items_page(self) -> None:
        """
        Browses the mechanics main page

        :return:
        """

        self.browse(self.items_wiki_base_url)
        # TODO: change it to dynamic wait
        time.sleep(1)
        self.accept_cookies()

    def browse_neutral_items_page(self) -> None:
        self.browse(self.neutral_items_wiki_base_url)
        # TODO: change it to dynamic wait
        time.sleep(1)
        self.accept_cookies()

    def get_main_page_elem(self) -> WebElement:
        """
        Retrieves the main page element that the information can be found on
        :return:
        """
        main_page_elem = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'mw-parser-output'))
        )

        self.main_page_elem = main_page_elem
        return main_page_elem

    def get_main_elem_children(self):

        # if the main_page_elem is None retrieve it first
        if self.main_page_elem is None:
            self.get_main_page_elem()

        children = self.main_page_elem.find_elements(By.XPATH, './*')
        children_useful_info = []
        for child in children:
            useful_info = {
                'id': child.get_attribute('id'),
                'class': child.get_attribute('class'),
                'text': child.text,
                'tag_name': child.tag_name,
            }
            children_useful_info.append(useful_info)
        # TODO: main_elem_children_processed to be removed
        self.main_elem_children_processed = children_useful_info
        self.main_elem_children = children

    def get_item_names_from_elem(self, elem: WebElement):
        pattern = re.compile(r"^(.*?)\s*\(\d+\s*\)$")
        return [pattern.match(item).group(1) for item in elem.text.split('\n') if pattern.match(item)]

    def get_all_shop_item_names(self):

        if self.main_page_elem is None:
            self.get_main_page_elem()

        if self.main_elem_children is None:
            self.get_main_elem_children()

        all_shop_item_names = []
        categories = ['consumables', 'attributes', 'equipment', 'miscellaneous', 'secret shop', 'accessories',
                      'support', 'magical', 'armor', 'weapons', 'armaments']
        for i, elem in enumerate(self.main_elem_children):
            if elem.tag_name == 'h3':
                if elem.text.lower().replace('[edit]','').strip() in categories:
                    all_shop_item_names.extend(self.get_item_names_from_elem(self.main_elem_children[i+1]))

        return all_shop_item_names

    def get_all_neutral_item_names(self):
        if self.main_page_elem is None:
            self.get_main_page_elem()

        if self.main_elem_children is None:
            self.get_main_elem_children()

        # TODO: implement neutral items names retrieval
        print()

    def scrape_all_items(self, path: str) -> None:

        self.browse_items_page()
        self.get_all_shop_item_names()
        self.browse_neutral_items_page()
        self.get_all_neutral_item_names()

if __name__ == '__main__':
    items_scraper = ItemsScraper()
    items_scraper.scrape_all_items('mechanics')