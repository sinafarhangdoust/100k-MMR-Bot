from typing import Literal

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

HEROES = Literal[
    # Strength
    "alchemist", "axe", "bristleback", "centaur_warrunner", "chaos_knight", "clockwerk", "dawnbreaker",
    "doom", "dragon_knight", "earth_spirit", "earthshaker", "elder_titan", "huskar", "kunkka",
    "legion_commander", "lifestealer", "lycan", "mars", "night_stalker", "ogre_magi", "omniknight",
    "phoenix", "primal_beast", "pudge", "slardar", "spirit_breaker", "sven", "tidehunter", "timbersaw",
    "tiny", "treant_protector", "tusk", "underlord", "undying", "wraith_king",

    # Agility
    "anti_mage", "bloodseeker", "bounty_hunter", "broodmother", "clinkz", "drow_ranger", "ember_spirit",
    "faceless_void", "gyrocopter", "hoodwink", "juggernaut", "kez", "lone_druid", "luna", "medusa", "meepo",
    "mirana", "monkey_king", "morphling", "naga_siren", "phantom_assassin", "phantom_lancer", "razor",
    "riki", "shadow_fiend", "slark", "sniper", "templar_assassin", "terrorblade", "troll_warlord",
    "ursa", "vengeful_spirit", "viper", "weaver",

    # Intelligence
    "ancient_apparition", "chen", "crystal_maiden", "dark_seer", "dark_willow", "disruptor", "enchantress",
    "grimstroke", "invoker", "jakiro", "keeper_of_the_light", "leshrac", "lich", "lina", "lion", "muerta",
    "necrophos", "oracle", "outworld_destroyer", "puck", "pugna", "queen_of_pain", "ringmaster", "rubick",
    "shadow_demon", "shadow_shaman", "silencer", "skywrath_mage", "storm_spirit", "tinker", "warlock",
    "winter_wyvern", "witch_doctor", "zeus",

    # Universal
    "abaddon", "arc_warden", "bane", "batrider", "beastmaster", "brewmaster", "dazzle", "death_prophet",
    "enigma", "io", "magnus", "marci", "natures_prophet", "nyx_assassin", "pangolier", "sand_king",
    "snapfire", "spectre", "techies", "venomancer", "visage", "void_spirit", "windranger"
]

MECHANICS = Literal[
    'abilities', 'accuracy', 'agility', 'ancient', 'armor manipulation', 'armor', 'armory', 'attack damage',
    'attack range', 'attack speed', 'attack animation', 'attack backswing', 'attack immunity', 'attack point',
    'attributes', 'aura', 'ban', 'banish', 'barracks', 'barrier', 'bash', 'basic dispel', 'blind', 'blink', 'break',
    'buildings', 'buyback', 'cast animation', 'cast backswing', 'cast point', 'channeling', 'chat wheel', 'cheats',
    'collision size', 'commend', 'console commands', 'controls', 'cooldown', 'courier', 'creep control techniques',
    'creeps', 'critical strike', 'custom games', 'cyclone', 'damage barrier', 'damage block', 'damage types',
    'damage amplification', 'damage manipulation', 'damage negation', 'damage over time', 'damage reduction',
    'debuff immunity', 'denying', 'disarm', 'disassembling', 'disjoint', 'drop list', 'effective hp', 'ethereal',
    'evasion', 'events', 'experience', 'expose', 'farming', 'fear', 'flying vision', 'forced movement', 'game map',
    'game modes', 'ganking', 'gems', 'gifting', 'gold', 'ground vision', 'hp removal', 'hud', 'health regeneration',
    'health', 'hex', 'hidden', 'hide', 'hotkeys', 'hypnosis', 'illusions', 'initiating', 'instant attack',
    'intelligence', 'invisibility', 'invulnerability', 'item drop system', 'item sharing', 'items', 'jungle',
    'jungling', 'lane creeps', 'lanes', 'launch options', 'leash', 'lifesteal', 'magic resistance', 'magical damage',
    'mana regeneration', 'mana break', 'mana', 'matchmaking rating', 'minimap', 'modding', 'movement speed', 'music',
    'mute', 'neutral creeps', 'outposts', 'patches', 'phased', 'physical damage', 'player behavior summary', 'priority',
    'projectile speed', 'pseudo-random distribution', 'pure damage', 'pushing', 'quality', 'rarity', 'recipes',
    'replay', 'report', 'restoration manipulation', 'roles', 'root', 'runes', 'scan', 'shackle', 'shared vision',
    'shops', 'silence', 'slow resistance', 'slow', 'spectating', 'spell damage', 'spell amplification', 'spell damage',
    'spell immunity', 'spell lifesteal', 'status resistance', 'steam market', 'strength', 'strong dispel', 'stun',
    'summons', 'talents', 'taunt', 'teleport', 'time of day', 'total attack damage', 'towers', 'trading', 'trap',
    'trees', 'true strike', 'true random distribution', 'true sight', 'turn rate', 'versions', 'vision', 'wards'
]

ITEMS = Literal[""]
