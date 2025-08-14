import os
import time
from urllib.parse import urljoin
from typing import List, Tuple
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
        self.neutral_items_wiki_base_url = "https://liquipedia.net/dota2/Neutral_Items"

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

    def get_main_elem_children(self) -> None:

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

    @staticmethod
    def get_shop_item_names_from_elem(elem: WebElement) -> List[str]:
        pattern = re.compile(r"^(.*?)\s*\(\d+\s*\)$")
        return [pattern.match(item).group(1) for item in elem.text.split('\n') if pattern.match(item)]

    @staticmethod
    def get_neutral_item_names_from_elem(elem: WebElement) -> List[str]:
        return [item.strip() for item in elem.text.split('\n')]

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
                    all_shop_item_names.extend(self.get_shop_item_names_from_elem(self.main_elem_children[i+1]))

        return all_shop_item_names

    @staticmethod
    def _norm(s: str) -> str:
        # lower, trim, and drop the “[edit]” clutter once
        return re.sub(r'\[edit\]', '', s or '', flags=re.IGNORECASE).strip().casefold()

    def get_all_neutral_item_names(self) -> Tuple[List[str], List[str]]:

        self.get_main_page_elem()
        self.get_main_elem_children()

        neutral_items = []
        enchantments = []
        item_categories = ['tier 1', 'tier 2', 'tier 3', 'tier 4', 'tier 5']
        enchantments_categories = ['tier 1-4', 'tier 2-3', 'tier 2-4', 'tier 4-5', 'tier 5']
        sections = {
            "active artifacts": (item_categories, neutral_items),
            "active enchantments": (enchantments_categories, enchantments),
        }

        children = self.main_elem_children
        current_key = None

        for i, elem in enumerate(children):
            text = self._norm(getattr(elem, "text", ""))
            tag = getattr(elem, "tag_name", "").lower()

            if tag == "h2":
                # enter a section if it matches any key (substring, case-insensitive)
                current_key = next((k for k in sections if k in text), None)
                continue

            if current_key and tag == "h3":
                allowed_categories, output_list = sections[current_key]
                if text in allowed_categories and i + 1 < len(children):
                    output_list.extend(self.get_neutral_item_names_from_elem(children[i + 1]))

        return sections["active artifacts"][1], sections["active enchantments"][1]

    def scrape_item_text(self, item_title: str) -> str | None:
        try:
            logger.info(f"Starting to scrape {item_title}")
            self.browse(urljoin(self.dota_wiki_base_url, item_title))
            text = self.get_main_page_elem().text
            logger.info(f"Finished scraping {item_title}")
            return text
        except Exception as err:
            logger.error(f"failed to scrape mechanic: {item_title}")
            logger.error(f"The following error occurred: {err}")

    def scrape_all_items(self, path: str) -> None:

        items_categories_texts = {
            'shop_items': [],
            'neutral_items': [],
            'enchantments': [],
        }
        self.browse_items_page()
        shop_items = self.get_all_shop_item_names()
        self.browse_neutral_items_page()
        neutral_items , enchantments = self.get_all_neutral_item_names()

        for item in shop_items:
            items_categories_texts['shop_items'].append({'name': item, 'text': self.scrape_item_text(item)})

        for item in neutral_items:
            items_categories_texts['neutral_items'].append({'name': item, 'text': self.scrape_item_text(item)})

        for enchantment in enchantments:
            items_categories_texts['enchantments'].append({'name': enchantment, 'text': self.scrape_item_text(enchantment)})

        if not os.path.exists(path):
            os.makedirs(path)

        for category, items_texts in items_categories_texts.items():
            category_path = os.path.join(path, category)
            if not os.path.exists(category_path):
                os.makedirs(category_path)
            for item_text in items_texts:
                with open(os.path.join(category_path, item_text['name'] + '.txt'), 'w') as item_file:
                        item_file.write(item_text['text'])


if __name__ == '__main__':
    items_scraper = ItemsScraper()
    items_scraper.scrape_all_items('items')