import requests
import json

# Fetch from OpenDota
hero_stats = requests.get("https://api.opendota.com/api/heroStats").json()
hero_abilities = requests.get("https://api.opendota.com/api/constants/hero_abilities").json()
abilities = requests.get("https://api.opendota.com/api/constants/abilities").json()
items = requests.get("https://api.opendota.com/api/constants/items").json()

# Compile all hero data
all_heroes = []

for hero in hero_stats:
    hero_key = hero["name"]
    ability_profile = hero_abilities.get(hero_key, {})

    # Abilities
    ability_names = ability_profile.get("abilities", [])
    detailed_abilities = [abilities[name] for name in ability_names if name in abilities]

    # Talents
    talents_raw = ability_profile.get("talents", [])
    detailed_talents = [abilities[t["name"]] for t in talents_raw if t["name"] in abilities]

    # Facets
    facets = ability_profile.get("facets", [])

    all_heroes.append({
        "hero": hero,
        "abilities": detailed_abilities,
        "talents": detailed_talents,
        "facets": facets
    })

with open("data/dota2_full_hero_item_data.json", "w") as f:
    json.dump({
        "heroes": all_heroes,
        "items": items
    }, f, indent=2)

print(" Saved: data/dota2_full_hero_item_data.json")
