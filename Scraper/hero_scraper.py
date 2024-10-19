import time
from urllib.parse import urljoin
from typing import Tuple, List, Dict
import re

from base_scraper import BaseScraper
from hero import Hero, Ability

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
        self.hero_summary_elems = None
        self.lore_summary_elem = None
        self.ability_elems = None
        self.hero = None

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

        hero_summary_elems = WebDriverWait(self.main_page_elem, 10).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME,
                 "table-responsive")
            )
        )
        self.hero_summary_elems = hero_summary_elems
        return hero_summary_elems

    def get_hero_lore_summary_elem(self) -> WebElement:
        """
        Retrieves the element that has the lore summary inside it
        :return:
        """

        # if the main_page_elem is None retrieve it first
        if self.main_page_elem is None:
            self.get_main_page_elem()

        lore_page_elem = WebDriverWait(self.main_page_elem, 10).until(
            EC.presence_of_element_located((By.ID, 'heroBio'))
        )
        self.lore_summary_elem = lore_page_elem
        return lore_page_elem

    def get_hero_ability_elems(self) -> Tuple[List[WebElement], List[WebElement]]:
        """
        Retrieves the elements that has the ability of the hero information inside it, if there are
         any additional elements at the end of the page it will also retrieve those
        :return:
        """

        # if the main_page_elem is None retrieve it first
        if self.main_page_elem is None:
            self.get_main_page_elem()

        ability_elems = WebDriverWait(self.browser, 10).until(
            EC.presence_of_all_elements_located((
                By.CSS_SELECTOR,
                'div[style*="display:flex; flex-wrap:wrap; align-items:flex-start;"]'))
        )
        self.ability_elems = []
        # TODO: better analyze the additional elems to capture all the possible cases
        additional_elems = []
        # filter only the actual ability elements, since they are other elements with te same
        # CSS_SELECTOR
        for elem in ability_elems:
            try:
                flag_element = elem.find_element(By.CLASS_NAME, 'ability-background')
                self.ability_elems.append(elem)
            except NoSuchElementException:
                # in case it's not the ability element remove it from the list of ability_elems
                additional_elems.append(elem)
                ability_elems.remove(elem)

        return ability_elems, additional_elems

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
                    base_mana_regen = stat_elem.text.split('+')[1].strip()
                    basic_stats['base_mana'] = base_mana
                    basic_stats['base_mana_regeneration'] = base_mana_regen
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
                # TODO: shoould be handled for the range heroes as well
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
                    night_movement_speed = stat_elem.text.strip().split('\nMove Speed')[0].split('/')[1].strip()
                    basic_stats['day_movement_speed'] = day_movement_speed
                    basic_stats['night_movement_speed'] = night_movement_speed
                elif stat_elem.find_element(By.TAG_NAME, 'a').get_attribute("title") == 'Turn Rate':
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
        for i, elem in enumerate(self.hero_summary_elems.find_elements(By.CSS_SELECTOR, 'tr')):
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
        hero_title = self.lore_summary_elem.find_element(By.XPATH, './/span').text
        if hero_title:
            self.hero.title = hero_title
        lore_rows = self.lore_summary_elem.find_elements(
            By.CSS_SELECTOR,
            "div[style='display:table-row;']"
        )
        hero_lore_summary = lore_rows[0].text.split('Lore: ')[1].strip()
        if hero_lore_summary:
            self.hero.lore_summary = hero_lore_summary
        return hero_title, hero_lore_summary

    def get_hero_lore_summary(self) -> None:
        """
        Auxiliary function for retrieving the hero lore summary element and processing the element
        to retrieve the lore text and the title of the hero
        :return:
        """
        self.get_hero_lore_summary_elem()
        self.process_hero_lore_summary_elem()

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

    def scrape_hero_page(self, hero_name) -> Hero:

        # create a new Hero object
        self.hero = Hero(hero_name)
        # browse the main hero page on wiki
        self.browse_hero_page(hero_name)
        # get the main page elem
        self.get_main_page_elem()
        # get the hero basic stats elem
        self.get_hero_basic_stats()
        # get the hero summary info
        self.get_hero_summary_info()
        # get the hero lore summary elem
        self.get_hero_lore_summary()

        self.get_hero_ability_elems()
        return self.hero



if __name__ == '__main__':
    hero_scraper = HeroScraper()
    hero_scraper.scrape_hero_page("axe")
    # hero_scraper.get_hero_ability_elems()
    print()

