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

        # Normalize header cells
        for th in soup.select("thead th"):
            label = th.get_text(" ", strip=True)
            a = th.find("a", title=True)
            if a and a.get("title") and a["title"] not in label:
                label = f"{label} {a['title']}".strip()
            th.string = label

        # robustly extract names from icon-only cells in first column
        for td in soup.select("tbody td:first-child"):
            names = []
            for a in td.select("a[title]"):
                t = (a.get("title") or "").strip()
                if t:
                    names.append(t)
            if not names:
                for img in td.select("img[alt]"):
                    t = (img.get("alt") or "").strip()
                    if t:
                        names.append(t)
            if not names:
                chosen = None
                for a in td.select("a[title]"):
                    text = a.get_text(strip=True)
                    href = a.get("href", "")
                    if text and href.startswith("/dota2/"):
                        chosen = a
                        break
                if not chosen:
                    anchors = [a for a in td.select("a") if a.get_text(strip=True)]
                    chosen = anchors[-1] if anchors else None
                if chosen:
                    names = [chosen.get_text(strip=True)]
                else:
                    names = [(td.get_text(" ", strip=True) or "-")]
            deduped = list(dict.fromkeys(names))
            td.clear()
            td.append(", ".join(deduped))
            # ----------------------------------------------------

            # --------- NEW: general, table-wide sanitation ---------
            # 1) Drop anything explicitly hidden (common sort keys live here)
        for el in soup.select("[style*='display:none'], [style*='visibility:hidden'], span.sortkey"):
            el.decompose()

            # 2) Prefer <abbr title="..."> over its visible text (numbers or expansions)
        for ab in soup.select("abbr[title]"):
            title = (ab.get("title") or "").strip()
            if title:
                ab.replace_with(title)

            # 3) After removing hidden nodes, strip any leftover leading sort codes like "a1", "b7", etc.
            #    Keep this conservative: only at start, letter+digits, then optional punctuation/space.
        import re
        for td in soup.select("tbody td"):
            text = td.get_text(" ", strip=True)
            cleaned = re.sub(r"^[A-Za-z]\d+(?=\s|/|,|\.|\d|$)\s*", "", text)
            if cleaned != text:
                td.clear()
                td.append(cleaned)
        # -------------------------------------------------------

        df = pd.read_html(StringIO(str(soup)), flavor="bs4", displayed_only=False)[0]
        df = df.astype("string")
        df.fillna("-", inplace=True)
        return '\n\n' + df.to_markdown(index=False) + '\n\n'

    @staticmethod
    def convert_skill_list_to_md(block_html) -> str:
        soup = BeautifulSoup(block_html, "lxml")
        root = soup.select_one("div.skilllist") or soup
        title_el = root.select_one(".skilllist-title")
        title = title_el.get_text(" ", strip=True) if title_el else None

        rows = []
        # Handle both simple (lite) and rich variants
        for li in root.select("li.skilllist-lite, li.skilllist-rich"):
            classes = li.get("class", [])
            if "skilllist-lite" in classes:
                # Collect only anchors that have visible text (skip the icon link)
                link_texts = []
                for a in li.select("a"):
                    t = a.get_text(" ", strip=True)
                    if t:  # ignore the <a> with only <img>
                        link_texts.append(t)

                if len(link_texts) >= 2:
                    source = link_texts[0]  # hero name
                    ability = link_texts[-1]  # ability name (may include superscript number)
                else:
                    # Fallback: split by en dash if weird markup
                    text = li.get_text(" ", strip=True)
                    parts = [p.strip() for p in text.split("–", 1)]
                    source = parts[0] if parts else ""
                    ability = parts[1] if len(parts) > 1 else ""
                details = ""
            else:
                # skilllist-rich
                head = li.select_one(".skilllist-rich-head")
                head_links = [a.get_text(" ", strip=True) for a in head.select("a")] if head else []
                source = head_links[0] if head_links else ""
                ability = head_links[-1] if len(head_links) >= 2 else ""
                desc = li.select_one(".skilllist-rich-desc")
                details = desc.get_text(" ", strip=True) if desc else ""

            rows.append((source, ability, details))

        # Build markdown
        heading = f"\n\n#### {title}\n\n" if title else "\n\n"
        df = pd.DataFrame(rows, columns=["Source", "Ability", "Details"]).astype("string").fillna("-")
        df = df.loc[:, (df != "").any(axis=0)]

        return heading + df.to_markdown(index=False) + "\n\n"

    @staticmethod
    def convert_heading_to_md(heading_el) -> str:
        level = int(heading_el.tag_name[1])  # "h2" → 2
        text = heading_el.get_attribute("textContent").strip()
        # Clamp level to a reasonable range (e.g. h1–h6 → #–######)
        level = min(max(level, 1), 6)
        return "\n\n" + ("#" * level) + " " + text + "\n\n"

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

    def process_skill_list(self, block_element):
        html = block_element.get_attribute("outerHTML")
        md = self.convert_skill_list_to_md(html)
        # Return the <pre> so we never touch the stale block handle again
        return self.browser.execute_script("""
            const el  = arguments[0];
            const md  = arguments[1];
            const pre = document.createElement('pre');
            pre.style.whiteSpace = 'pre-wrap';
            pre.style.margin = '0';
            pre.setAttribute('data-replaced-skilllist', '1');
            pre.textContent = md;   // keep literal markdown
            el.replaceWith(pre);
            return pre;
        """, block_element, md)

    def process_heading(self, heading_el):
        md = self.convert_heading_to_md(heading_el)
        return self.browser.execute_script("""
            const el  = arguments[0];
            const md  = arguments[1];
            const pre = document.createElement('pre');
            pre.style.whiteSpace = 'pre-wrap';
            pre.style.margin = '0';
            pre.setAttribute('data-replaced-heading', '1');
            pre.textContent = md;
            el.replaceWith(pre);
            return pre;
        """, heading_el, md)

    def remove_excess_elems(self):
        # Remove common non-content blocks inside the article body
        selectors = [
            "#toc",  # classic TOC (your example)
            ".toc",  # fallback TOC class
            ".vector-toc",  # Vector skin TOC
            "nav.vector-toc",  # Vector nav-based TOC
            ".mw-editsection",  # little [edit] links next to headings
            ".navigation-not-searchable",  # ad/aux boxes (present in your HTML)
            ".navbox",  # big footer nav templates
            ".content-ad",  # ad slots
            ".printfooter",  # “Retrieved from …”
            "#catlinks"  # categories
        ]
        for sel in selectors:
            try:
                for el in self.main_page_elem.find_elements(By.CSS_SELECTOR, sel):
                    self.browser.execute_script("arguments[0].remove()", el)
            except Exception:
                # Keep going even if a selector doesn't match on a page
                continue

    def scrape_mechanic_text(self, mechanic_title) -> str | None:
        try:
            logger.info(f"Starting to scrape {mechanic_title}")
            self.browse(urljoin(self.dota_wiki_base_url, mechanic_title))
            self.get_main_page_elem()
            self.remove_excess_elems()

            # tables
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
            # skill lists
            all_skill_lists = self.main_page_elem.find_elements(By.CSS_SELECTOR, "div.skilllist")
            skill_list_elements = [
                el for el in all_skill_lists
                if el.get_attribute("textContent")
                   and not self.browser.execute_script("return !!arguments[0].querySelector('div.skilllist')", el)
            ]
            skill_list_depths = [
                (self.browser.execute_script("let d=0,n=arguments[0]; while(n=n.parentElement){d++} return d;", el), el)
                for el in skill_list_elements
            ]
            # headings
            all_headings = self.main_page_elem.find_elements(By.CSS_SELECTOR, "h2, h3, h4, h5, h6")
            heading_depths = [
                (self.browser.execute_script("let d=0,n=arguments[0]; while(n=n.parentElement){d++} return d;", el), el)
                for el in all_headings
            ]
            for _, h in sorted(heading_depths, key=lambda x: x[0], reverse=True):
                try:
                    self.process_heading(h)
                except StaleElementReferenceException:
                    continue
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

        for _, block_el in sorted(skill_list_depths, key=lambda x: x[0], reverse=True):
            try:
                self.process_skill_list(block_el)
            except StaleElementReferenceException:
                continue
            except Exception as err:
                logger.error(f"failed to scrape mechanic: {mechanic_title}")
                logger.error(f"The following error occurred: {err}")

        text = self.main_page_elem.get_attribute("textContent")
        text = f"# {mechanic_title}\n\n" + text
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
    # TODO: fix the mechanic page titles that are actually sub page of another page
    mechanics_scraper = MechanicsScraper()
    mechanics_scraper.scrape_mechanics('mechanics')
