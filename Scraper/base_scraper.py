import logging
import time
from threading import Thread
from typing import List

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.driver_cache import DriverCacheManager
from selenium.webdriver.chrome.options import Options

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


class BaseScraper:
    """ The BaseScraper which can be used to scrape webpages with limited functionality """
    def __init__(
        self,
        chrome_options: str | List[str] = None,
        chrome_extensions: str | List[str] = None,
        tab_check_interval: float = 1.0,
        tab_check_duration: float = 10.0,
    ) -> None:
        """
        Initializes the BaseScraper
        :param chrome_options: the custom chrome options to use for the WebChromeDriver
        :param chrome_extensions: the custom extensions to use for the WebChromeDriver
        :param tab_check_interval: the internal to check to close any new tabs opened after
        the first lunch
        :param tab_check_duration: the duration to check to close any new tabs opened after the
        first lunch
        """
        default_chrome_options = [
            '--disable-search-engine-choice-screen',
            '--start-maximized'
        ]
        default_chrome_extensions = [
            '../chrome_extensions/ad_block_plus.crx'
        ]
        # set the default driver validity for 14 days since daily
        # updates of the driver might not be particularly stable
        self.driver_cache_manager = DriverCacheManager(valid_range=14)
        self.chrome_driver_manager = ChromeDriverManager(cache_manager=self.driver_cache_manager)
        self.service = Service(self.chrome_driver_manager.install())
        self.chrome_options = Options()
        # set the default chrome options and extensions
        self._set_chrome_options(chrome_options=default_chrome_options)
        self._set_chrome_extensions(chrome_extensions=default_chrome_extensions)
        # set the custom chrome options and extensions
        if chrome_options is not None:
            self._set_chrome_options(chrome_options=chrome_options)
        if chrome_extensions is not None:
            self._set_chrome_extensions(chrome_extensions=chrome_extensions)
        self.browser = webdriver.Chrome(
            service=self.service,
            options=self.chrome_options
        )
        self.tab_check_interval = tab_check_interval
        self.tab_check_duration = tab_check_duration
        self.keep_checking_tabs = True
        # close any extra tabs opened by the extensions
        self.tab_check_thread = Thread(target=self._periodic_tab_check)
        self.tab_check_thread.start()

    def _set_chrome_options(
        self,
        chrome_options: str | List[str]
    ) -> None:
        """
        Sets the options for the ChromeWebDriver
        :param chrome_options: the chrome options can be a single option or a list of options
        :return: None
        """
        if type(chrome_options) is str:
            self.chrome_options.add_argument(chrome_options)

        if type(chrome_options) is list:
            for opt in chrome_options:
                self.chrome_options.add_argument(opt)

    def _set_chrome_extensions(
        self,
        chrome_extensions: str | List[str]
    ) -> None:
        """
        sets the extensions for the ChromeWebDriver
        :param chrome_extensions: the chrome extensions can be a single extension or a list of
        extensions
        :return:
        """
        if type(chrome_extensions) is str:
            self.chrome_options.add_extension(chrome_extensions)

        if type(chrome_extensions) is list:
            for ext in chrome_extensions:
                self.chrome_options.add_extension(ext)

    def _periodic_tab_check(self):
        """
        Periodically checks for and closes extra tabs.
        """
        end_time = time.time() + self.tab_check_duration
        while time.time() < end_time and self.keep_checking_tabs:
            self._close_extra_tabs()
            time.sleep(self.tab_check_interval)

    def _close_extra_tabs(self):
        """
        Closes any additional tabs, keeping only the first one open.
        """
        if len(self.browser.window_handles) > 1:
            main_window = self.browser.window_handles[0]
            for handle in self.browser.window_handles[1:]:
                self.browser.switch_to.window(handle)
                self.browser.close()
            self.browser.switch_to.window(main_window)

    def browse(
        self,
        url: str
    ) -> None:
        """
        visits the given url
        :param url: the url to visit
        :return:
        """
        self.browser.get(url)

    def remove_ads(self) -> None:
        """
        Removes ads from the page by hiding iframes and common
        ad containers without affecting page interactivity.
        """
        # Hide iframes
        all_iframes = self.browser.find_elements(By.TAG_NAME, "iframe")
        if len(all_iframes) > 0:
            print("Ads Found\n")
            self.browser.execute_script("""
                var elems = document.getElementsByTagName("iframe");
                for(var i = 0, max = elems.length; i < max; i++) {
                    elems[i].style.visibility = 'hidden';
                    elems[i].style.pointerEvents = 'none';
                }
            """)
            logger.info('Total Ads (iframes): ' + str(len(all_iframes)))

        # Hide common ad containers by class
        ad_classes = [
            "adsbygoogle", "ad-container", "ad-wrapper", "google-auto-placed", "sponsored"
        ]

        for ad_class in ad_classes:
            ads = self.browser.find_elements(By.CLASS_NAME, ad_class)
            if len(ads) > 0:
                self.browser.execute_script("""
                    var elems = document.getElementsByClassName("{ad_class}");
                    for(var i = 0, max = elems.length; i < max; i++) {
                        elems[i].style.visibility = 'hidden';
                elems[i].style.pointerEvents = 'none';
                }
                """)
                logger.info(f'Total Ads (class "{ad_class}"): ' + str(len(ads)))

        # Hide ads by ID
        ad_ids = [
            "top-ad", "bottom-ad", "sidebar-ad", "header-ad", "footer-ad"
        ]

        for ad_id in ad_ids:
            ad_element = self.browser.find_elements(By.ID, ad_id)
            if len(ad_element) > 0:
                self.browser.execute_script("""
                    var elem = document.getElementById("{ad_id}");
                    if (elem) {
                        elem.style.visibility = 'hidden';
                elem.style.pointerEvents = 'none';
                }
                """)
                logger.info(f'Total Ads (ID "{ad_id}"): ' + str(len(ad_element)))
        self.browser.refresh()
        logger.info('Ad removal completed.')