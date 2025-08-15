import os
import time
from io import StringIO
from urllib.parse import urljoin
from typing import List, Dict

from base_scraper import BaseScraper

from custom_logger.custom_logger import ChatDota2Logger

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import pandas as pd
from bs4 import BeautifulSoup


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

    def get_all_mechanics_titles(self) -> List[Dict]:

        # if the main_page_elem is None retrieve it first
        if self.main_page_elem is None:
            self.get_main_page_elem()

        if self.main_elem_children is None:
            self.get_main_elem_children()

        main_categories = {}
        logger.info("Starting to scrape all mechanics titles")
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
                    if '/' in main_mechanic_title:
                        for split in main_mechanic_title.split('/'):
                            category_mechanics.append({split: sub_mechanic_titles})
                    elif "Head-up display (HUD)" in main_mechanic_title:
                        main_mechanic_title = "HUD"
                        category_mechanics.append({main_mechanic_title: sub_mechanic_titles})
                    else:
                        category_mechanics.append({main_mechanic_title: sub_mechanic_titles})
                except Exception:
                    continue

            mechanic_titles.append({category: category_mechanics})

        logger.info(f"Found {len(mechanic_titles)} mechanics titles")
        logger.info("Finished scraping mechanics titles")

        self.mechanic_titles = mechanic_titles
        return mechanic_titles

    @staticmethod
    def convert_table_to_md(table_html) -> str:
        soup = BeautifulSoup(table_html, "lxml")
        soup = (
        soup.select_one("table.mw-datatable")
        or soup.select_one("table.sortable")
        or soup.select_one("table:has(thead)")
        or soup.find_all("table")[-1]
        )

        # Make <th> text like "Base Strength", "+ Strength / LVL", "L30 Strength", etc.
        for th in soup.select("thead th"):
            label = th.get_text(" ", strip=True)
            a = th.find("a", title=True)
            if a and a["title"] and a["title"] not in label:
                label = f"{label} {a['title']}".strip()
            th.string = label

        # First column: keep the hero name text
        for td in soup.select("tbody td:first-child"):
            # Prefer an <a> that points to a /dota2/... page and has visible text
            chosen = None
            for a in td.select("a[title]"):
                text = a.get_text(strip=True)
                href = a.get("href", "")
                if text and href.startswith("/dota2/"):
                    chosen = a
                    break
            # Fallback: last <a> with any non-empty text
            if not chosen:
                anchors = [a for a in td.select("a") if a.get_text(strip=True)]
                chosen = anchors[-1] if anchors else None

            if chosen:
                td.clear()
                # Plain name:
                td.append(chosen.get_text(strip=True))
                # OR, if you want Markdown links instead, use:
                # name, href = chosen.get_text(strip=True), chosen.get("href", "")
                # td.append(f"[{name}]({href})")
            else:
                td.string = td.get_text(" ", strip=True)

        df = pd.read_html(StringIO(str(soup)), flavor="bs4", displayed_only=False)[0]
        df = df.astype("string")
        df.fillna("-", inplace=True)

        return '\n\n' + df.to_markdown(index=False) + '\n\n'

    def process_table(self, table_element):
        html_element = table_element.get_attribute('outerHTML')
        table_text = self.convert_table_to_md(html_element)
        self.browser.execute_script("""
                            const table = arguments[0];
                            const md    = arguments[1];
                            table.scrollIntoView({behavior: 'instant', block: 'center'});  // optional
                            const pre   = document.createElement('pre');
                            pre.style.whiteSpace = 'pre-wrap';
                            pre.style.margin = '0';
                            pre.setAttribute('data-replaced-table', '1');
                            pre.textContent = md;   // literal markdown
                            table.replaceWith(pre);
                            return pre;
                        """, table_element, table_text)

    def remove_excess_elems(self):

        classes_to_remove = ['navigation-not-searchable', 'navbox']
        try:
            for class_to_remove in classes_to_remove:
                elem_to_remove = self.main_page_elem.find_element(By.CLASS_NAME, class_to_remove)
                self.browser.execute_script("arguments[0].remove()", elem_to_remove)
        except Exception:
            pass

    def scrape_mechanic_text(self, mechanic_title) -> str | None:
        try:
            logger.info(f"Starting to scrape {mechanic_title}")
            self.browse(urljoin(self.dota_wiki_base_url, mechanic_title))
            self.get_main_page_elem()
            self.remove_excess_elems()
            all_tables = self.main_page_elem.find_elements(By.TAG_NAME, "table")
            table_elements = [
                el for el in all_tables
                if el.get_attribute("textContent")
                   and not self.browser.execute_script("return !!arguments[0].querySelector('table')", el)
            ]
            depth_pairs = [
                (self.browser.execute_script(
                    "let d=0,n=arguments[0]; while(n=n.parentElement){d++} return d;", el
                ), el)
                for el in table_elements
            ]
        except Exception as err:
            logger.error(f"failed to scrape mechanic: {mechanic_title}")
            logger.error(f"The following error occurred: {err}")
            return None
        for _, table_el in sorted(depth_pairs, key=lambda x: x[0], reverse=True):
            try:
                self.process_table(table_el)
            except StaleElementReferenceException:
                # If something else mutated the DOM between snapshot and now, just skip
                continue
            except Exception as err:
                logger.error(f"failed to scrape mechanic: {mechanic_title}")
                logger.error(f"The following error occurred: {err}")
        text = self.main_page_elem.get_attribute("textContent")
        logger.info(f"Finished scraping {mechanic_title}")
        return text

    def scrape_mechanics(self, path: str) -> None:
        self.browse_mechanics_page()
        self.get_all_mechanics_titles()

        mechanics_text = {}
        for category_dict in self.mechanic_titles:
            for category, mechanic_list in category_dict.items():
                for mechanics_dict in mechanic_list:
                    for main_mechanic_title, sub_mechanic_titles in mechanics_dict.items():
                        # retrieve the main_mechanic_title details
                        mechanics_text[main_mechanic_title] = self.scrape_mechanic_text(main_mechanic_title)
                        # retrieve the sub_mechanic_title details if available any
                        if sub_mechanic_titles:
                            for sub_mechanic_title in sub_mechanic_titles:
                                mechanics_text[sub_mechanic_title] = self.scrape_mechanic_text(sub_mechanic_title)

        if not os.path.exists(path):
            os.makedirs(path)
        for mechanic_title, mechanic_text in mechanics_text.items():
            if mechanic_text:
                with open(os.path.join(path, f"{mechanic_title}.md"), 'w') as mechanic_file:
                    mechanic_file.write(mechanic_text)


if __name__ == '__main__':
    mechanics_scraper = MechanicsScraper()
    mechanics_scraper.scrape_mechanics('mechanics')
