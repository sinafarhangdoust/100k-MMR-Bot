import json
import os
import time
from urllib.parse import urljoin
from typing import Tuple, List, Dict

from base_scraper import BaseScraper
from hero import Hero

from custom_logger.custom_logger import ChatDota2Logger

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException


logger = ChatDota2Logger()

class MechanicsScraper(BaseScraper):
    def __init__(self, **kwargs):

        super().__init__(**kwargs)
        self.dota_wiki_base_url = "https://liquipedia.net/dota2/"
        self.mechanics_wiki_base_url = "https://liquipedia.net/dota2/Mechanics"

        self.main_page_elem = None
        self.main_elem_children = None
        # TODO: main_elem_children_processed to be removed
        self.main_elem_children_processed = None
        self.mechanic_titles = None

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


    def browse_mechanics_page(self) -> None:
        """
        Browses the mechanics main page

        :return:
        """

        self.browse(self.mechanics_wiki_base_url)
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

    def get_all_mechanics_titles(self) -> List[Dict]:

        # if the main_page_elem is None retrieve it first
        if self.main_page_elem is None:
            self.get_main_page_elem()

        if self.main_elem_children is None:
            self.get_main_elem_children()

        main_categories = {}
        for elem in self.main_elem_children:
            if elem.tag_name.startswith('h'):
                main_category = (elem.text.replace('[edit]', '').strip())
            if elem.tag_name.startswith('table'):
                main_categories[main_category] = elem

        mechanic_titles = []
        for category, elem in main_categories.items():
            rows = elem.find_elements(By.CSS_SELECTOR, "tbody tr")
            category_mechanics = []
            for row in rows:
                try:
                    # TODO: handle Autocase mechanic
                    cols = row.find_elements(By.TAG_NAME, "td")
                    main_mechanic_title = cols[0].find_element(By.TAG_NAME, 'b').text.strip()
                    sub_mechanic_titles = [cat.text.strip() for cat in cols[0].find_elements(By.TAG_NAME, 'li')]
                    category_mechanics.append({main_mechanic_title: sub_mechanic_titles})
                except Exception:
                    continue

            mechanic_titles.append({category: category_mechanics})

        self.mechanic_titles = mechanic_titles
        return mechanic_titles

    def scrape_mechanics(self):
        self.browse_mechanics_page()
        self.get_all_mechanics_titles()


if __name__ == '__main__':
    mechanics_scraper = MechanicsScraper()
    mechanics_scraper.scrape_mechanics()
    print()