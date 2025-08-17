import aiohttp, asyncio, re
from typing import Dict, List, Tuple
import math

#TODO cache hero_matchups() results in memory for the session (dict of cid -> list) with a TTL; OpenDota’s free tier is limited
#TODO Role filter: add role=offlane to only show counters that fit your lineup (roles come from heroStats).
#TODO UI polish: add quick-reply buttons to “Lock in” a suggested hero and keep a running pick/ban board.


CDN = "https://cdn.cloudflare.steamstatic.com"
HEROES: Dict[int, dict] = {}
NAME_TO_ID: Dict[str, int] = {}
HERO_IMG: Dict[int, str] = {}

def _norm(s: str) -> str:
    return re.sub("r[^a-z0-9]"+"", s.lower())

async def _get_json(url: str):
    async with aiohttp.ClientSession() as s:
        async  with s.get(url, timeout =20) as r:
            r.raise_for_status()
            return await r.json()


#TODO: Change this to use localised SCRAPED DATA
async def init_heroes():
    """
    Loads heroStats once: includes localized_name, 'name', roles, img/icon, id
    """
    global HEROES, NAME_TO_ID, HERO_IMG
    data = await _get_json("https://api.opendota.com/api/heroStats")
    HEROES = {}
    NAME_TO_ID = {}
    HERO_IMG = {}
    for h in data:
        hid = h["id"]
        HEROES[hid] = h
        # name keys
        loc = h.get("localized_name") or ""
        raw = (h.get("name") or "").replace("npc_dota_hero_", "")
        for key in {loc, raw, f"{raw}"}:
            if key:
                NAME_TO_ID.setdefault(_norm(key), hid)
        # portrait url (OpenDota's 'img' is a path)
        if h.get("img"):
            HERO_IMG[hid] = f'{CDN}{h["img"]}'

async def hero_matchups(hero_id: int) -> List[dict]:
    """
    Returns list of { hero_id, games_played, wins } vs that hero_id (OpenDota)
    """
    return await _get_json(f"https://api.opendota.com/api/heroes/{hero_id}/matchups")


def resolve_hero_ids(names: List[str]) -> List[int]:
    ids = []
    for n in names:
        k = _norm(n)
        if k in NAME_TO_ID:
            ids.append(NAME_TO_ID[k])
    return ids




async def counter_scores(enemy_ids: List[int], exclude_ids: List[int]) -> List[Tuple[int, float, int]]:
    """
    For each candidate hero not already picked/banned (exclude_ids),
    compute a simple counter score vs enemy_ids using matchup winrates.

    Score = sum_over_enemies( (wins/gp - 0.5) * log(1+gp) )
    Returns list of (hero_id, score, total_samples) sorted desc.
    """
    # Build lookup: for each candidate hero C, we need stats vs each enemy E.
    # OpenDota's matchups endpoint is "for hero=C, list vs all others".
    results = []
    for cid, h in HEROES.items():
        if cid in exclude_ids:
            continue
        try:
            m = await hero_matchups(cid)
        except Exception:
            continue
        by_enemy = {row["hero_id"]: row for row in m}
        score = 0.0
        samples = 0
        for eid in enemy_ids:
            row = by_enemy.get(eid)
            if not row:
                continue
            gp = row.get("games_played", 0) or row.get("games", 0) or 0
            wins = row.get("wins", 0)
            if gp <= 0:
                continue
            wr = wins / gp
            score += (wr - 0.5) * math.log1p(gp)
            samples += gp
        results.append((cid, score, samples))
    results.sort(key=lambda x: (x[1], x[2]), reverse=True)
    return results