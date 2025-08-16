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
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from bs4 import BeautifulSoup

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

    @staticmethod
    def convert_heading_to_md(heading_el) -> str:
        level = int(heading_el.tag_name[1])  # "h2" → 2
        text = heading_el.get_attribute("textContent").strip()
        # Clamp level to a reasonable range (e.g. h1–h6 → #–######)
        level = min(max(level, 1), 6)
        return "\n\n" + ("#" * level) + " " + text + "\n\n"

    @staticmethod
    def convert_item_infobox_to_md(html: str) -> str:

        def _maybe_seconds(label: str, value: str) -> str:
            if label.strip().lower() == "stock" and re.fullmatch(r"\d+(?:\.\d+)?", value):
                return f"{value} seconds"
            return value

        def sanitize_cell(node, prefer_abbr_title: bool = True):
            for el in node.select("[style*='display:none'], [style*='visibility:hidden'], span.sortkey"):
                el.decompose()

            # Use abbr TITLE or TEXT depending on context
            for ab in node.select("abbr[title]"):
                if prefer_abbr_title:
                    t = (ab.get("title") or "").strip()
                else:
                    t = (ab.get_text(" ", strip=True) or "").strip()
                if t:
                    ab.replace_with(t)

            for icon in node.select("span[title]"):
                tt = (icon.get("title") or "").strip()
                if tt in {"Yes", "No"}:
                    icon.replace_with(tt)

            for br in node.find_all("br"):
                br.replace_with(" · ")

            for img in node.find_all("img"):
                if img.get("alt"):
                    img.replace_with(img["alt"])
                else:
                    img.decompose()

            text = re.sub(r"\s+", " ", node.get_text(" ", strip=True)).strip()
            text = re.sub(r"^[A-Za-z]\d+(?=\s|/|,|\.|\d|$)\s*", "", text)
            return text

        # ---------- NEW: include “Recipe” when parsing the diagram rows ----------
        def parse_recipe_block(recipe_header_tr, current_title: str):
            titles = []
            consumed_tr_ids = set()

            tr = recipe_header_tr.find_next_sibling("tr")
            steps = 0
            while tr is not None and steps < 3:
                anchors = tr.select("a[title]")
                if not anchors:
                    break
                for a in anchors:
                    t = (a.get("title") or "").strip()
                    # strip trailing costs e.g. "Recipe (650)" -> "Recipe"
                    t = re.sub(r"\s*\(\d+(?:\.\d+)?\)\s*$", "", t)
                    if t:
                        titles.append(t)  # keep Recipe!
                consumed_tr_ids.add(id(tr))
                tr = tr.find_next_sibling("tr")
                steps += 1

            ordered = list(dict.fromkeys(titles))

            builds_from, upgrades_into = [], []
            if current_title and current_title in ordered:
                idx = ordered.index(current_title)
                upgrades_into = ordered[:idx]
                builds_from = ordered[idx + 1:]
            else:
                upgrades_into = ordered

            return builds_from, upgrades_into, consumed_tr_ids

        # ------------------------------------------------------------------------

        soup = BeautifulSoup(html, "lxml")
        box = soup.select_one("table.fo-nttax-infobox-wrapper.fo-nttax-infobox")
        if not box:
            return ""

        # Title
        title_el = box.select_one("th > div > div[style*='text-align:center']")
        title = ""
        if title_el:
            ab = title_el.find("abbr")
            if ab:
                title = (ab.get_text(" ", strip=True) or ab.get("title") or "").strip()
            else:
                title = title_el.get_text(" ", strip=True)

        # Flavor
        flavor = ""
        italic_td = box.find("td", attrs={"style": re.compile(r"font-style:\s*italic", re.I)})
        if italic_td:
            flavor = italic_td.get_text(" ", strip=True)

        detail = box.select_one("table[style*='text-align:left']")
        if not detail:
            hdr = f"### {title}\n\n" if title else ""
            flav = f"> {flavor}\n\n" if flavor else ""
            return hdr + flav

        rows = []
        last_label = None
        skip_tr_ids = set()
        deferred_recipe_rows = []

        for tr in detail.select("tr"):
            if id(tr) in skip_tr_ids:
                continue

            th = tr.find("th")
            tds = tr.find_all("td")

            # Section header (colspan)
            if th and th.has_attr("colspan"):
                header_raw = (th.get_text(" ", strip=True) or "").strip().lower()

                if header_raw == "recipe":
                    builds_from, upgrades_into, consumed = parse_recipe_block(tr, title)
                    skip_tr_ids |= consumed
                    if builds_from:
                        deferred_recipe_rows.append(("Builds From", " + ".join(builds_from)))
                    if upgrades_into:
                        deferred_recipe_rows.append(("Upgrades Into", ", ".join(upgrades_into)))
                    continue

                section = sanitize_cell(th)
                if section:
                    rows.append(("— " + section + " —", ""))
                continue

            # Regular row
            if th and tds:
                label = sanitize_cell(th, prefer_abbr_title=False)  # prefer visible text for labels
                value_td = tds[-1]
                value = sanitize_cell(value_td)
                value = _maybe_seconds(label, value)

                if label:
                    rows.append((label, value))
                    last_label = label
                else:
                    if rows and rows[-1][0] == last_label:
                        rows[-1] = (last_label, (rows[-1][1] + " · " + value) if rows[-1][1] else value)
                    else:
                        rows.append((last_label or "", value))
                continue

            # Continuation lines (rowspan)
            if not th and len(tds) >= 1 and last_label:
                value = sanitize_cell(tds[-1])
                value = _maybe_seconds(last_label, value)
                if rows and rows[-1][0] == last_label:
                    rows[-1] = (last_label, (rows[-1][1] + " · " + value) if rows[-1][1] else value)
                else:
                    rows.append((last_label, value))

        rows.extend(deferred_recipe_rows)

        out = []
        if title:
            out.append(f"### {title}\n\n")
        if flavor:
            out.append(f"> {flavor}\n\n")
        if rows:
            out.append("| Property | Value |\n|---|---|\n")
            for k, v in rows:
                if k.startswith("— ") and k.endswith(" —"):
                    out.append(f"| *{k[2:-2].strip()}* | |\n")
                else:
                    out.append(f"| {k} | {v or '-'} |\n")
            out.append("\n")
        return "".join(out)

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

    def process_item_infobox(self, infobox_el):
        html = infobox_el.get_attribute("outerHTML")
        md = self.convert_item_infobox_to_md(html)
        return self.browser.execute_script("""
            const md  = arguments[1];
            const pre = document.createElement('pre');
            pre.style.whiteSpace = 'pre-wrap';
            pre.style.margin = '0';
            pre.setAttribute('data-replaced-infobox', '1');
            pre.textContent = md;
            arguments[0].replaceWith(pre);
            return pre;
        """, infobox_el, md)

    def scrape_item_text(self, item_title: str) -> str | None:
        try:
            logger.info(f"Starting to scrape {item_title}")
            self.browse(urljoin(self.dota_wiki_base_url, item_title))
            self.get_main_page_elem()
            self.remove_excess_elems()

            try:
                all_headings = self.main_page_elem.find_elements(By.CSS_SELECTOR, "h2, h3, h4, h5, h6")
                heading_depths = [
                    (self.browser.execute_script("let d=0,n=arguments[0]; while(n=n.parentElement){d++} return d;", el),
                     el)
                    for el in all_headings
                ]
                infoboxes = self.main_page_elem.find_elements(
                    By.CSS_SELECTOR,
                    "table.fo-nttax-infobox-wrapper.fo-nttax-infobox, table.fo-nttax-infobox"
                )
                infobox_depths = [
                    (self.browser.execute_script("let d=0,n=arguments[0]; while(n=n.parentElement){d++} return d;", el),
                     el)
                    for el in infoboxes
                ]
                for _, h in sorted(heading_depths, key=lambda x: x[0], reverse=True):
                    try:
                        self.process_heading(h)
                    except StaleElementReferenceException:
                        continue
                for _, ib in sorted(infobox_depths, key=lambda x: x[0], reverse=True):
                    try:
                        self.process_item_infobox(ib)
                    except StaleElementReferenceException:
                        continue
            except Exception as err:
                logger.error(f"failed to scrape item: {item_title}")
                logger.error(f"The following error occurred: {err}")
                return None

            text = self.get_main_page_elem().get_attribute('textContent')
            logger.info(f"Finished scraping {item_title}")
            return text
        except Exception as err:
            logger.error(f"failed to scrape item: {item_title}")
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
                with open(os.path.join(category_path, item_text['name'] + '.md'), 'w') as item_file:
                        item_file.write(item_text['text'])


if __name__ == '__main__':
    items_scraper = ItemsScraper()
    items_scraper.scrape_all_items('items')