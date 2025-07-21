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


class HeroScraper(BaseScraper):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)
        self.dota_wiki_base_url = "https://liquipedia.net/dota2/"
        self.dota_official_base_url = "https://dota2.com"

        self.main_page_elem = None
        self.basic_stats_elem = None
        self.hero_summary_elem = None
        self.lore_summary_elems = None
        self.talent_tree_elem = None
        self.innate_elem = None
        self.upgrades_elem = None
        self.ability_elems = None
        self.main_elem_children = None
        # TODO: main_elem_children_processed to be removed
        self.main_elem_children_processed = None
        self.hero = None
        self.heroes = None

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

    def browse_hero_page(
        self,
        hero_name: str
    ) -> None:
        """
        Browses the given hero page
        :param hero_name: the name of the hero to browse
        :return:
        """

        hero_url = urljoin(self.dota_wiki_base_url, hero_name)
        self.browse(hero_url)
        # TODO: change it to dynamic wait
        time.sleep(1)
        self.accept_cookies()

    def browse_heroes_page(self):
        heroes_url = urljoin(self.dota_wiki_base_url, 'heroes')
        self.browse(heroes_url)
        # TODO: change it to dynamic wait
        time.sleep(1)
        self.accept_cookies()

    def get_all_hero_names(self) -> List[str]:
        self.browse_heroes_page()
        self.get_main_page_elem()
        hero_elements = self.main_page_elem.find_elements(By.CSS_SELECTOR, ".heroes-panel__hero-card__title a")
        hero_names = [el.text for el in hero_elements]
        return hero_names

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

    def get_hero_basic_stats_elem(self) -> WebElement:
        """
        Retrieves the table of basic stats for the hero
        :return:
        """
        # if the main_page_elem is None retrieve it first
        if self.main_page_elem is None:
            self.get_main_page_elem()

        basic_stats_elem = WebDriverWait(self.main_page_elem, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR,
                 "div[style*='float:right;'][style*='border:1px solid grey;']")
            )
        )
        self.basic_stats_elem = basic_stats_elem
        return basic_stats_elem

    def get_hero_summary_elem(self) -> WebElement:
        """
        Retrieves the hero summary element that includes the summary information of the hero
        :return:
        """
        if self.main_page_elem is None:
            self.get_main_page_elem()

        hero_summary_elem = WebDriverWait(self.main_page_elem, 10).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME,
                 "table-responsive")
            )
        )
        self.hero_summary_elem = hero_summary_elem
        return hero_summary_elem

    def get_hero_lore_summary_elems(self) -> List[WebElement]:
        """
        Retrieves the elements that has the lore summary inside it
        :return:
        """

        if self.main_elem_children is None:
            self.get_main_elem_children()

        lore_summary_elems = []
        lore_summary_elem_indices = []
        for i, elem in enumerate(self.main_elem_children):
            if elem.tag_name == 'h2' and elem.text.lower().startswith('bio'):
                lore_summary_elem_indices.extend([i+1, i+2])
            if lore_summary_elem_indices and i in lore_summary_elem_indices:
                lore_summary_elems.append(elem)

        self.lore_summary_elems = lore_summary_elems
        return lore_summary_elems

    def get_hero_facet_elems(self) -> List[WebElement]:
        """
        Retrieves the element that has the facet information inside it
        :return:
        """
        # if the main_page_elem is None retrieve it first
        if self.main_page_elem is None:
            self.get_main_page_elem()

        hero_facet_elems = WebDriverWait(self.main_page_elem, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.facetBox[id]'))
        )
        self.hero_facet_elems = hero_facet_elems
        return hero_facet_elems

    def get_hero_upgrades_elem(self) -> List[WebElement]:
        """
        Retrieves the element that has the upgrades info inside it
        :return:
        """

        if self.main_elem_children is None:
            self.get_main_elem_children()

        upgrades_elem = None

        for i, elem in enumerate(self.main_elem_children):
            if elem.tag_name == 'h3' and elem.text.lower().startswith("aghanim's"):
                upgrades_elem = self.main_elem_children[i+1]

        self.upgrades_elem = upgrades_elem
        return upgrades_elem

    def get_hero_ability_elems(self) -> List[WebElement]:
        """
        Retrieves the elements that has the ability of the hero information inside it
        :return:
        """

        def check_elem_ability(elem: WebElement):
            found = False
            for ability_name in self.hero.summary_info['abilities']:
                if elem.text.lower().startswith(ability_name.lower()):
                    found = True
                    break
            return found and elem.tag_name == 'h3'

        if self.main_elem_children is None:
            self.get_main_elem_children()

        starting_idx = 0
        ability_elems = []
        for i, elem in enumerate(self.main_elem_children):
            if elem.tag_name == 'h2' and elem.text.lower().startswith('abilities'):
                starting_idx = i + 1

        for i, elem in enumerate(self.main_elem_children[starting_idx:]):
            if check_elem_ability(elem):
                ability_elems.append(self.main_elem_children[starting_idx + i + 1])

        self.ability_elems = ability_elems
        return ability_elems

    def get_hero_talent_tree_elem(self) -> WebElement:

        if self.main_elem_children is None:
            self.get_main_elem_children()

        talent_tree_elem = None
        talent_tree_elem_idx = None
        for i, elem in enumerate(self.main_elem_children):
            if ((elem.tag_name == 'h3' or elem.tag_name == 'h2') and
                    elem.text.lower().startswith('talents')):
                talent_tree_elem_idx = i + 1
            if talent_tree_elem_idx is not None and i == talent_tree_elem_idx:
                talent_tree_elem = elem

        self.talent_tree_elem = talent_tree_elem
        return talent_tree_elem

    def get_hero_innate_elem(self) -> WebElement:

        if self.main_elem_children is None:
            self.get_main_elem_children()

        innate_elem = None
        innate_elem_idx = None
        for i, elem in enumerate(self.main_elem_children):
            if elem.tag_name == 'h2' and elem.text.lower().startswith('innate'):
                innate_elem_idx = i + 2
            if innate_elem_idx is not None and i == innate_elem_idx:
                innate_elem = elem

        self.innate_elem = innate_elem
        return innate_elem

    def extract_attributes_from_basic_stats(self) -> Dict:
        """
        Primary and secondary attributes, the values of those attributes and the attribute gain
        per each level
        :return:
        """
        attributes = {}
        attribute_order_mapping = {}
        attribute_elem = self.basic_stats_elem.find_element(
            By.CSS_SELECTOR,
            "div[style*='color:white;'][style*='text-align:center;'][style*='font-weight:bold;'][style*='text-shadow:1px 1px 2px #000;']"
        )
        # find the primary and secondary attributes
        for i, attribute in enumerate(attribute_elem.find_elements(By.XPATH, './/div[@id]')):
            attribute_name = attribute.find_element(By.TAG_NAME, 'a').get_attribute(
                "title").strip().lower()
            if attribute.get_attribute('id') == 'primaryAttribute':
                attributes[attribute_name] = {'type': 'primary'}
            else:
                attributes[attribute_name] = {'type': 'secondary'}
            attribute_order_mapping[i] = attribute_name
        # assign the base and gain for the primary and secondary attributes
        for i, attribute_value in enumerate(attribute_elem.find_elements(
                By.CSS_SELECTOR,
                "div[style*='color:#FFF;'][style*='text-shadow:1px 1px 2px #000;']")
        ):
            attribute_name = attribute_order_mapping[i]
            base_attribute = attribute_value.text.split('+')[0].strip()
            attribute_gain = attribute_value.text.split('+')[1].strip()
            attributes[attribute_name].update(
                {
                    'base_attribute': base_attribute,
                    'attribute_gain': attribute_gain
                }
            )
        return attributes

    def process_spellcard_wrapper(self, spellcard_wrapper: WebElement):
        """
        Given a Selenium WebElement for <div class="spellcard-wrapper">,
        extract all relevant fields into a dict.
        """
        spellcard = spellcard_wrapper.find_element(By.CSS_SELECTOR, ".spellcard")

        data = {}

        # — Name & Hotkeys —
        # find the header row that has the bold span (ability/facet name)
        header_span = spellcard.find_element(
            By.XPATH,
            ".//div[contains(@style,'border-bottom')]/span[contains(@style,'font-weight:bold')]"
        )
        data["name"] = header_span.text.strip()

        # any hotkey badges (Default Hotkey, Legacy Keys, etc.)
        hotkeys = []
        for hk in spellcard.find_elements(
                By.XPATH,
                ".//div[@title='Default Hotkey' or @title='Legacy Keys']"
        ):
            key = hk.find_element(By.TAG_NAME, "span").text.strip()
            hotkeys.append({
                "type": hk.get_attribute("title"),
                "key": key
            })
        if hotkeys:
            data["hotkeys"] = hotkeys

        # — Icon —
        # pick the first image in a div whose class starts with "target_"
        # icon_img = spellcard.find_element(
        #     By.CSS_SELECTOR,
        #     "div[class^='target_'] img"
        # )
        # data["icon"] = icon_img.get_attribute("src")

        # — Ability metadata (Ability / Affects) —
        meta = {}
        for label in spellcard.find_elements(By.CSS_SELECTOR, ".spelltad"):
            value = label.find_element(
                By.XPATH,
                "following-sibling::*[@class='spelltad_value']"
            ).text.strip()
            meta[label.text.strip()] = value
        if meta:
            data["metadata"] = meta

        # — Main description —
        # look for the flex-box right after metadata that holds the text
        try:
            desc = spellcard.find_element(
                By.XPATH,
                ".//div[contains(@style,'display:flex')][.//img]/div[last()]"
            ).text.strip()
            data["description"] = desc
        except:
            pass

        # — Numeric traits (e.g. Radius, Armor Bonus per Kill…) —
        traits = {}
        for t in spellcard.find_elements(By.CLASS_NAME, "spelltrait_value"):
            parts = t.text.split(":", 1)
            name = parts[0].strip()
            val = parts[1].strip() if len(parts) > 1 else ""
            traits[name] = val
        if traits:
            data["traits"] = traits

        # — Extra/descriptive blocks (spelldesc) —
        extras = []
        for blk in spellcard.find_elements(By.CSS_SELECTOR, ".spelldesc"):
            # usually the second inner <div> holds the text
            divs = blk.find_elements(By.TAG_NAME, "div")
            if len(divs) >= 2:
                extras.extend([div.text.strip() for div in divs if div.text.strip()])
        if extras:
            data["extra_descriptions"] = extras

        # — Cooldown / Mana Cost table —
        costs = {}
        icons = spellcard.find_elements(By.CLASS_NAME, "spellcost_icon")
        vals = spellcard.find_elements(By.CLASS_NAME, "spellcost_value")
        for ico, val in zip(icons, vals):
            # the <a title="Cooldown"> or <a title="Mana Cost">
            try:
                lbl = ico.find_element(By.TAG_NAME, "a").get_attribute("title")
                costs[lbl] = val.text.strip()
            except:
                pass
        if costs:
            data["costs"] = costs

        # — Lore (if present) —
        try:
            lore = spellcard.find_element(By.CLASS_NAME, "spelllore").text.strip()
            data["lore"] = lore
        except:
            pass

        # — Tabs: Details / Interactions / Status Effects / Misc. —
        tabs = {}
        for tab_li in spellcard_wrapper.find_elements(By.CSS_SELECTOR, ".tabs-dynamic .nav-tabs li"):
            count = tab_li.get_attribute("data-count")
            title = tab_li.text.strip()
            # don't need to process show all
            if title.lower() == 'show all':
                break
            # find the matching content panel
            panel = spellcard_wrapper.find_element(
                By.CSS_SELECTOR,
                f".tabs-content .content{count}"
            )
            tabs[title] = panel.text.strip()
        if tabs:
            data["tabs"] = tabs

        return data

    def process_hero_basic_stats_elem(self) -> Dict:
        """
        Processes the hero basic stats element and extracts the following information from it:
        - Primary and secondary attributes, the values of those attributes and the attribute gain
        per each level
        - Base Armor
        - Base Magic Resistence
        - Base Damage
        - Projectile Speed
        - Attack Range
        - Attack Speed
        - Attack Animation
        - Base Movement Speed
        - Turn rate
        - Collision Size
        - Bound Radius
        - Vision Range
        - Gib Type
        - Release Date

        :return:
        """
        basic_stats = {}
        attributes = self.extract_attributes_from_basic_stats()
        basic_stats['attributes'] = attributes
        basic_stats_elems = self.basic_stats_elem.find_elements(By.CSS_SELECTOR, "tr")
        for stat_elem in basic_stats_elems:
            try:
                if stat_elem.find_element(By.TAG_NAME, 'a').get_attribute("title") == 'Health':
                    base_health = stat_elem.text.split('+')[0].strip()
                    base_health_regen = stat_elem.text.split('+')[1].strip()
                    basic_stats['base_health'] = base_health
                    basic_stats['base_health_regeneration'] = base_health_regen
                elif stat_elem.find_element(By.TAG_NAME, 'a').get_attribute("title") == 'Mana':
                    base_mana = stat_elem.text.split('+')[0].strip()
                    if base_mana != 'n/a':
                        base_mana_regen = stat_elem.text.split('+')[1].strip()
                        basic_stats['base_mana_regeneration'] = base_mana_regen
                    basic_stats['base_mana'] = base_mana
                elif stat_elem.find_element(By.TAG_NAME, 'a').get_attribute("title") == 'Armor':
                    # TODO: if needed can extract the base effective hp from armor
                    base_armor = stat_elem.text.split('\nArmor\n')[0].strip()
                    basic_stats['base_armor'] = base_armor
                elif stat_elem.find_element(By.TAG_NAME, 'a').get_attribute("title") == 'Magic Resistance':
                    # TODO: if needed can extract the base effective hp from magic resistence
                    basic_magic_res = stat_elem.text.split('\nMagic Resist\n')[0].strip()
                    basic_stats['base_magic_resistence'] = basic_magic_res
                elif stat_elem.find_element(By.TAG_NAME, 'a').get_attribute("title") == 'Main Attack Damage':
                    base_damage = stat_elem.text.split('\nDamage\n')[0].strip()
                    base_avg_damage = stat_elem.text.split('\nDamage\n')[1].strip()
                    basic_stats['base_damage'] = base_damage
                    basic_stats['base_average_damage'] = base_avg_damage
                elif stat_elem.find_element(By.TAG_NAME, 'a').get_attribute("title") == 'Projectile Speed':
                    projectile_speed = stat_elem.find_element(By.TAG_NAME, 'a').text.strip()
                    basic_stats['projectile_speed'] = projectile_speed
                # TODO: should be handled for the range heroes as well
                elif stat_elem.find_element(By.TAG_NAME, 'a').get_attribute("title") == 'Melee':
                    if stat_elem.text.strip():
                        attack_range, acquisition_range = stat_elem.text.strip().split('\nAttack Range\n')
                        basic_stats['attack_range'] = attack_range
                        basic_stats['acquisition_range'] = acquisition_range
                elif stat_elem.find_element(By.TAG_NAME, 'a').get_attribute("title") == 'Attack Speed':
                    attack_speed = stat_elem.find_element(By.CSS_SELECTOR, 'b').text.strip()
                    basic_stats['attack_speed'] = attack_speed
                elif stat_elem.find_element(By.TAG_NAME, 'a').get_attribute("title") == 'Attack Animation':
                    attack_animation = stat_elem.text.strip().split('\nAnimation')[0]
                    basic_stats['attack_animation'] = attack_animation
                elif 'Move Speed' in stat_elem.text:
                    day_movement_speed = stat_elem.text.strip().split('\nMove Speed')[0].split('/')[0].strip()
                    # night_movement_speed = stat_elem.text.strip().split('\nMove Speed')[0].split('/')[1].strip()
                    basic_stats['day_movement_speed'] = day_movement_speed
                    # basic_stats['night_movement_speed'] = night_movement_speed
                elif stat_elem.find_element(By.TAG_NAME, 'a').get_attribute("title") == 'Turn Rate':
                    if not basic_stats.get('turn_rate'):
                        turn_rate = stat_elem.text.strip().split('\nTurn Rate')[0].strip()
                        basic_stats['turn_rate'] = turn_rate
                elif stat_elem.find_element(By.TAG_NAME, 'a').get_attribute("title") == 'Collision Size':
                    collision_size = stat_elem.text.strip().split('\nCollision Size')[0].strip()
                    basic_stats['collision_size'] = collision_size
                elif stat_elem.find_element(By.TAG_NAME, 'a').get_attribute("title") == 'Bound Radius':
                    bound_radius = stat_elem.text.strip().split('\nBound Radius')[0].strip()
                    basic_stats['bound_radius'] = bound_radius
                elif 'Vision Range' in stat_elem.text:
                    day_vision_range = stat_elem.text.split('\nVision Range')[0].strip().split('/')[0].strip()
                    night_vision_range = stat_elem.text.split('\nVision Range')[0].strip().split('/')[1].strip()
                    basic_stats['day_vision_range'] = day_vision_range
                    basic_stats['night_vision_range'] = night_vision_range
            # TODO: Gib type, Released and Competitive Span can be extracted
            except NoSuchElementException:
                logger.error('Could not find the desired element')

        return basic_stats

    def process_hero_summary_elem(self) -> Dict:
        """
        Processes the hero summary elem and extracts the following information from it:
        - Hero Summary
        - Roles
        - Complexity
        - Adjectives

        :return:
        """
        summary_info = {}
        summary = ''
        for i, elem in enumerate(self.hero_summary_elem.find_elements(By.CSS_SELECTOR, 'tr')):
            if elem.text:
                if 'Roles' in elem.text:
                    roles = []
                    for role_elem in elem.find_elements(By.TAG_NAME, 'a'):
                        if role_elem.get_attribute("title") == 'Role':
                            roles.append(role_elem.text.strip())
                    summary_info['roles'] = roles
                elif 'Complexity' in elem.text:
                    complexity = str(len([cplx_elem for cplx_elem in elem.find_elements(By.CSS_SELECTOR, 'td')])) + '/3'
                    summary_info['complexity'] = complexity
                elif 'Adjectives' in elem.text:
                    adjectives = elem.find_element(By.CSS_SELECTOR, 'td').text.split('\nLegs ')[0].split(',')
                    num_legs = elem.find_element(By.CSS_SELECTOR, 'td').text.split('\nLegs ')[1]
                    summary_info['adjectives'] = adjectives
                    summary_info['num_legs'] = num_legs
                else:
                    summary += elem.text + '\n'
            else:
                # extract ability names from the icon row
                abilities = []
                for link in elem.find_elements(By.XPATH, ".//a[starts-with(@href, '#') and @title]"):
                    name = link.get_attribute("title").strip()
                    if name and name not in abilities:
                        abilities.append(name)
                summary_info['abilities'] = abilities

        summary_info['summary'] = summary
        return summary_info

    def process_hero_lore_summary_elem(self) -> Tuple[str, str]:
        """
        Processes the hero lore summary element and extracts the hero title and hero lore summary
        from it
        :return:
        """
        hero_title = ""
        hero_lore_summary = ""
        hero_title = self.lore_summary_elems[0].find_element(
            By.CLASS_NAME, 'quote-source'
        ).text.strip()
        if hero_title:
            self.hero.title = hero_title
        lore_rows = self.lore_summary_elems[1].find_elements(
            By.CSS_SELECTOR,
            'div[style*="display:table-row"]'
        )
        [row for row in lore_rows if 'Lore: ' in row.text]
        hero_lore_summary = [row for row in lore_rows if 'Lore: ' in row.text][0].text.split('Lore: ')[1].strip()
        if hero_lore_summary:
            self.hero.lore_summary = hero_lore_summary
        return hero_title, hero_lore_summary

    def process_hero_facet_elems(self) -> Dict:
        facets = {}
        for elem in self.hero_facet_elems:
            facet_name = elem.find_element(By.CLASS_NAME, "facetLink").text.strip()
            facet_desc = elem.find_element(By.CLASS_NAME, "facetCell").text.strip()
            facets[facet_name] = {'description': facet_desc}

        return facets

    def process_hero_upgrades_elem(self) -> Dict:
        """

        :return:
        """
        # Grab all the upgrade titles in order (first Scepter, then Shard)
        titles = self.upgrades_elem.find_elements(By.CSS_SELECTOR, ".aghupgTitle")
        # Grab all the description elements under any .aghupgShadow
        descs = self.upgrades_elem.find_elements(By.CSS_SELECTOR, ".aghupgShadow .aghupgDesc")

        upgrades = {}
        # First title + first desc → Scepter
        if len(titles) >= 1 and len(descs) >= 1:
            upgrades[titles[0].text.strip()] = descs[0].text.strip()
            self.hero.scepter_upgrade_info = descs[0].text.strip()
        # The remaining descs all belong to the Shard section
        if len(titles) >= 2 and len(descs) > 1:
            shard_texts = [d.text.strip() for d in descs[1:]]
            # join multiple entries with a blank line
            upgrades[titles[1].text.strip()] = "\n\n".join(shard_texts)
            self.hero.shard_upgrade_info = "\n\n".join(shard_texts)

        return upgrades

    def process_hero_ability_elems(self) -> List:
        abilities = []
        for elem in self.ability_elems:
            if elem.text:
                ability = self.process_spellcard_wrapper(elem)
                abilities.append(ability)

        self.hero.abilities = abilities
        return abilities

    def process_hero_talent_tree_elem(self):

        table = self.talent_tree_elem.find_element(By.CSS_SELECTOR, "div > table.wikitable")

        talent_tree = {}

        # iterate over each row
        for row in table.find_elements(By.TAG_NAME, "tr"):
            # skip header/footer rows that use colspan
            if row.find_elements(By.XPATH, "./th[@colspan]"):
                continue

            # find the three cells: left <td>, middle <th>, right <td>
            tds = row.find_elements(By.TAG_NAME, "td")
            ths = row.find_elements(By.XPATH, "./th[not(@colspan)]")
            if len(tds) == 2 and len(ths) == 1:
                # parse the talent value
                key = int(ths[0].text.strip())

                # extract and clean the descriptions
                left_desc = tds[0].text.strip()
                right_desc = tds[1].text.strip()

                talent_tree[key] = {
                    "left": left_desc,
                    "right": right_desc
                }
        return talent_tree

    def process_hero_innate_elem(self):
        innate_info = self.process_spellcard_wrapper(self.innate_elem)
        self.hero.innate = innate_info
        return innate_info

    def get_hero_basic_stats(self):
        """
        Auxiliary function for retrieving the hero basic stats element and processing the element
        to retrieve the following information which will be part of hero.basic_stats:
        - Primary and secondary attributes, the values of those attributes and the attribute gain
        per each level
        - Base Armor
        - Base Magic Resistence
        - Base Damage
        - Projectile Speed
        - Attack Range
        - Attack Speed
        - Attack Animation
        - Base Movement Speed
        - Turn rate
        - Collision Size
        - Bound Radius
        - Vision Range
        - Gib Type
        - Release Date

        :return:
        """

        self.get_hero_basic_stats_elem()
        basic_stats = self.process_hero_basic_stats_elem()
        self.hero.basic_stats = basic_stats

    def get_hero_summary_info(self):
        self.get_hero_summary_elem()
        summary_info = self.process_hero_summary_elem()
        self.hero.summary_info = summary_info

    def get_hero_facets(self):
        """

        :return:
        """
        self.get_hero_facet_elems()
        facets = self.process_hero_facet_elems()
        self.hero.facets = facets

    def get_hero_upgrades(self):
        self.get_hero_upgrades_elem()
        self.process_hero_upgrades_elem()

    def get_hero_talent_tree(self):

        self.get_hero_talent_tree_elem()
        talent_tree = self.process_hero_talent_tree_elem()
        self.hero.talent_tree = talent_tree

    def get_hero_lore_summary(self) -> None:
        """
        Auxiliary function for retrieving the hero lore summary element and processing the element
        to retrieve the lore text and the title of the hero
        :return:
        """
        self.get_hero_lore_summary_elems()
        self.process_hero_lore_summary_elem()

    def get_hero_innate(self):
        """

        :return:
        """
        self.get_hero_innate_elem()
        self.process_hero_innate_elem()

    def get_hero_abilities(self):
        self.get_hero_ability_elems()
        self.process_hero_ability_elems()

    def scrape_hero_page(self, hero_name) -> Hero:

        # create a new Hero object
        self.hero = Hero(hero_name)
        # browse the main hero page on wiki
        self.browse_hero_page(hero_name)
        # get the main page elem
        self.get_main_page_elem()
        # get the main element children
        self.get_main_elem_children()
        # get the hero basic stats elem
        self.get_hero_basic_stats()
        # get the hero summary info
        self.get_hero_summary_info()
        # get the hero facets
        self.get_hero_facets()
        # get hero upgrades
        self.get_hero_upgrades()
        # get hero talent tree
        self.get_hero_talent_tree()
        # get the hero lore summary
        self.get_hero_lore_summary()
        # get the hero innate
        # TODO: some heroes have facet descriptions after innate description as well
        self.get_hero_innate()
        # TODO: get the hero model
        # get hero abilities
        self.get_hero_abilities()

        return self.hero

    def scrape_all_heroes(self, path: str):
        self.heroes = []
        if not os.path.exists(path):
            os.makedirs(path)
        hero_names = self.get_all_hero_names()
        for hero_name in hero_names:
            try:
                logger.info(f"Starting to scrape {hero_name}")
                # check if the hero is already scraped, if so skip it
                if os.path.exists(os.path.join(path, hero_name + '.json')):
                    logger.info("%s hero data already exists" % hero_name)
                    continue
                self.scrape_hero_page('_'.join(hero_name.lower().split(' ')))
                # save the hero on filesystem
                with open(os.path.join(path, f"{hero_name}.json"), 'w') as hero_file:
                    json.dump(
                        self.hero.to_dict(),
                        hero_file,
                        indent=4,
                        ensure_ascii=False,
                    )
                self.heroes.append(self.hero)
                logger.info(f"Successfully finished scraping {hero_name}")
            except Exception as err:
                logger.error(f"failed to scrape hero: %s", hero_name)
                logger.error("The following error occurred: %s", err)
        return self.heroes



if __name__ == '__main__':
    hero_scraper = HeroScraper()
    hero_scraper.scrape_hero_page("sven")
    # hero_scraper.scrape_all_heroes("/Users/sinafarhangdoust/personal_projects/ChatDota2/hero_data")
