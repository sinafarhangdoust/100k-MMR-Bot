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
    'Abilities', 'Accuracy', 'Agility', 'Ancient', 'Armor Manipulation', 'Armor', 'Armory', 'Attack Damage',
    'Attack Range', 'Attack Speed', 'Attack animation', 'Attack backswing', 'Attack immunity', 'Attack point',
    'Attributes', 'Aura', 'Ban', 'Banish', 'Barracks', 'Barrier', 'Bash', 'Basic dispel', 'Blind', 'Blink', 'Break',
    'Buildings', 'Buyback', 'Cast animation', 'Cast backswing', 'Cast point', 'Channeling', 'Chat wheel', 'Cheats',
    'Collision Size', 'Commend', 'Console commands', 'Controls', 'Cooldown', 'Courier', 'Creep control techniques',
    'Creeps', 'Critical strike', 'Custom Games', 'Cyclone', 'Damage Barrier', 'Damage Block', 'Damage Types',
    'Damage amplification', 'Damage manipulation', 'Damage negation', 'Damage over time', 'Damage reduction',
    'Debuff immunity', 'Denying', 'Disarm', 'Disassembling', 'Disjoint', 'Drop list', 'Effective HP', 'Ethereal',
    'Evasion', 'Events', 'Experience', 'Expose', 'Farming', 'Fear', 'Flying vision', 'Forced movement', 'Game map',
    'Game modes', 'Ganking', 'Gems', 'Gifting', 'Gold', 'Ground vision', 'HP Removal', 'HUD', 'Health Regeneration',
    'Health', 'Hex', 'Hidden', 'Hide', 'Hotkeys', 'Hypnosis', 'Illusions', 'Initiating', 'Instant Attack',
    'Intelligence', 'Invisibility', 'Invulnerability', 'Item drop system', 'Item sharing', 'Items', 'Jungle',
    'Jungling', 'Lane creeps', 'Lanes', 'Launch Options', 'Leash', 'Lifesteal', 'Magic Resistance', 'Magical Damage',
    'Mana Regeneration', 'Mana break', 'Mana', 'Matchmaking Rating', 'Minimap', 'Modding', 'Movement Speed', 'Music',
    'Mute', 'Neutral creeps', 'Outposts', 'Patches', 'Phased', 'Physical Damage', 'Player Behavior Summary', 'Priority',
    'Projectile speed', 'Pseudo-random distribution', 'Pure Damage', 'Pushing', 'Quality', 'Rarity', 'Recipes',
    'Replay', 'Report', 'Restoration Manipulation', 'Roles', 'Root', 'Runes', 'Scan', 'Shackle', 'Shared vision',
    'Shops', 'Silence', 'Slow Resistance', 'Slow', 'Spectating', 'Spell Damage', 'Spell amplification', 'Spell damage',
    'Spell immunity', 'Spell lifesteal', 'Status Resistance', 'Steam Market', 'Strength', 'Strong dispel', 'Stun',
    'Summons', 'Talents', 'Taunt', 'Teleport', 'Time of day', 'Total Attack Damage', 'Towers', 'Trading', 'Trap',
    'Trees', 'True Strike', 'True random distribution', 'True sight', 'Turn Rate', 'Versions', 'Vision', 'Wards'
]

ITEMS = Literal[""]
