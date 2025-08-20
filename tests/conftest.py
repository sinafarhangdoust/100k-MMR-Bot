import asyncio
import pytest
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
@pytest.fixture(scope="session")
def event_loop():
    # pytest-asyncio needs an event loop fixture on Windows sometimes
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_hero_stats():
    # Minimal heroStats set: three heroes with roles & images
    # IDs are arbitrary but consistent across matchups below.
    return [
        {
            "id": 1,
            "name": "npc_dota_hero_antimage",
            "localized_name": "Anti-Mage",
            "roles": ["Carry", "Escape"],
            "img": "/apps/dota2/images/dota_react/heroes/antimage.png?"
        },
        {
            "id": 2,
            "name": "npc_dota_hero_pudge",
            "localized_name": "Pudge",
            "roles": ["Disabler", "Durable", "Initiator"],
            "img": "/apps/dota2/images/dota_react/heroes/pudge.png?"
        },
        {
            "id": 3,
            "name": "npc_dota_hero_storm_spirit",
            "localized_name": "Storm Spirit",
            "roles": ["Carry", "Escape", "Nuker"],
            "img": "/apps/dota2/images/dota_react/heroes/storm_spirit.png?"
        },
        {
            "id": 4,
            "name": "npc_dota_hero_axe",
            "localized_name": "Axe",
            "roles": ["Initiator", "Durable", "Disabler"],
            "img": "/apps/dota2/images/dota_react/heroes/axe.png?"
        },
    ]


@pytest.fixture
def sample_matchups():
    # For each candidate hero (key), list of dicts vs others:
    # Use fields: hero_id, games_played, wins
    # We want Anti-Mage (1) to be a *worse* counter than Axe (4) vs Pudge (2) + Storm (3)
    return {
        1: [  # Anti-Mage vs others
            {"hero_id": 2, "games_played": 300, "wins": 150},  # 50% vs Pudge
            {"hero_id": 3, "games_played": 250, "wins": 110},  # 44% vs Storm
            {"hero_id": 4, "games_played": 200, "wins": 100},
        ],
        4: [  # Axe vs others
            {"hero_id": 2, "games_played": 400, "wins": 230},  # 57.5% vs Pudge
            {"hero_id": 3, "games_played": 300, "wins": 165},  # 55% vs Storm
            {"hero_id": 1, "games_played": 200, "wins": 110},
        ],
        2: [  # Pudge vs others
            {"hero_id": 1, "games_played": 300, "wins": 150},
            {"hero_id": 3, "games_played": 300, "wins": 140},
            {"hero_id": 4, "games_played": 300, "wins": 130},
        ],
        3: [  # Storm vs others
            {"hero_id": 1, "games_played": 250, "wins": 140},
            {"hero_id": 2, "games_played": 300, "wins": 160},
            {"hero_id": 4, "games_played": 300, "wins": 130},
        ],
    }
