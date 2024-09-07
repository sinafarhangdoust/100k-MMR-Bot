from enum import Enum

DEFAULT_CHROME_OPTIONS = [
    '--disable-search-engine-choice-screen',
    '--start-maximized'
]
DEFAULT_CHROME_EXTENSIONS = [
    '../chrome_extensions/ad_block_plus.crx'
]
ADBLOCK_EXTENSION_URL = ('https://www.crx4chrome.com/go.php?p=31928&i=cfhdojbkjhnklbpkdaibdccddilif'
                         'ddb&s=O3CUdPpTCIbEs&l=https%3A%2F%2Ff6.crx4chrome.com%2Fcrx.php%3Fi%3Dcfh'
                         'dojbkjhnklbpkdaibdccddilifddb%26v%3D4.6')


class MainAttributes(Enum):
    str = 'Strength'
    dex = 'Dexterity'
    intel = 'Intelligence'
    uni = 'Universal'


HEROES = {
    MainAttributes.str.value: [],
    MainAttributes.dex.value: [],
    MainAttributes.intel.value: [],
    MainAttributes.uni.value: []
}
