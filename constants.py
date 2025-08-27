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

ITEM_TYPE = Literal['shop_items', 'neutral_items', 'enchantment']

SHOP_ITEMS = Literal[
    'Alert Enchantment', 'Keen-Eyed Enchantment', 'Audacious Enchantment', 'Mystical Enchantment',
    'Boundless Enchantment', 'Quickened Enchantment', 'Brawny Enchantment', 'Timeless Enchantment',
    'Crude Enchantment', 'Titanic Enchantment', 'Evolved Enchantment', 'Tough Enchantment',
    'Feverish Enchantment', 'Vampiric Enchantment', 'Fleetfooted Enchantment', 'Vast Enchantment',
    'Greedy Enchantment', 'Wise Enchantment'
]
NEUTRAL_ITEMS = Literal[
    "book of the dead", "brigand's blade", "chipped vest", "crippling crossbow", "dezun bloodrite", "divine regalia",
    "dormant curio", "essence ring", "fallen sky", "gale guard", "giant's maul", "gunpowder gauntlet",
    "helm of the undying", "jidi pollen bag", "kobold cup", "magnifying monocle", "mana draught", "minotaur horn",
    "occult bracelet", "outworld staff", "pollywog charm", "poor man's shield", "psychic headband", "pyrrhic cloak",
    "ripper's lash", "searing signet", "serrated shiv", "sister's shroud", "spark of courage", "spider legs",
    "stygian desolator", "tumbler's toy", "unrelenting eye", "whisper of the dread",
]
ENCHANTMENT_ITEMS = Literal[
    "abyssal blade", "aeon disk", "aether lens", "aghanim's scepter", "aghanim's shard", "arcane blink", "arcane boots",
    "armlet of mordiggian", "assault cuirass", "band of elvenskin", "battle fury", "belt of strength", "black king bar",
    "blade mail", "blade of alacrity", "blades of attack", "blink dagger", "blitz knuckles", "blood grenade",
    "bloodstone", "bloodthorn", "boots of bearing", "boots of speed", "boots of travel", "bottle", "bracer",
    "broadsword", "buckler", "butterfly", "chainmail", "circlet", "clarity", "claymore", "cloak", "cornucopia",
    "crimson guard", "crown", "crystalys", "daedalus", "dagon", "demon edge", "desolator", "diadem", "diffusal blade",
    "disperser", "divine rapier", "dragon lance", "drum of endurance", "dust of appearance", "eaglesong", "echo sabre",
    "enchanted mango", "energy booster", "eternal shroud", "ethereal blade", "eul's scepter of divinity",
    "eye of skadi", "faerie fire", "falcon blade", "fluffy hat", "force staff", "gauntlets of strength",
    "gem of true sight", "ghost scepter", "gleipnir", "glimmer cape", "gloves of haste", "guardian greaves",
    "hand of midas", "harpoon", "headdress", "healing salve", "heart of tarrasque", "heaven's halberd",
    "helm of iron will", "helm of the dominator", "helm of the overlord", "holy locket", "hurricane pike", "hyperstone",
    "infused raindrops", "iron branch", "javelin", "kaya and sange", "kaya", "khanda", "linken's sphere", "lotus orb",
    "maelstrom", "mage slayer", "magic stick", "magic wand", "manta style", "mantle of intelligence", "mask of madness",
    "mekansm", "meteor hammer", "mithril hammer", "mjollnir", "monkey king bar", "moon shard", "morbid mask",
    "mystic staff", "nullifier", "null talisman", "oblivion staff", "observer ward", "octarine core", "ogre axe",
    "orb of blight", "orb of corrosion", "orb of frost", "orb of venom", "orchid malevolence", "overwhelming blink",
    "parasma", "pavise", "perseverance", "phase boots", "phylactery", "pipe of insight", "platemail", "point booster",
    "power treads", "quelling blade", "radiance", "reaver", "refresher orb", "revenant's brooch", "ring of basilius",
    "ring of health", "ring of protection", "ring of regen", "ring of tarrasque", "robe of the magi", "rod of atos",
    "sacred relic", "sage's mask", "sange and yasha", "sange", "satanic", "scythe of vyse", "sentry ward",
    "shadow amulet", "shadow blade", "shiva's guard", "silver edge", "skull basher", "slippers of agility",
    "smoke of deceit", "solar crest", "soul booster", "soul ring", "spirit vessel", "staff of wizardry", "swift blink",
    "talisman of evasion", "tango", "tiara of selemene", "town portal scroll", "tranquil boots", "ultimate orb",
    "urn of shadows", "vanguard", "veil of discord", "vitality booster", "vladmir's offering", "void stone",
    "voodoo mask", "wind lace", "wind waker", "witch blade", "wraith band", "yasha and kaya", "yasha",
]
