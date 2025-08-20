import aiohttp, asyncio, re, math
from typing import Dict, List, Tuple, Optional
from cachetools import TTLCache  # NEW

CDN = "https://cdn.cloudflare.steamstatic.com"
HEROES: Dict[int, dict] = {}
NAME_TO_ID: Dict[str, int] = {}
HERO_IMG: Dict[int, str] = {}

# NEW: per-hero matchup cache (≈200 heroes total; 6h TTL)
_MATCHUPS_CACHE = TTLCache(maxsize=400, ttl=6 * 60 * 60)

# tools/opendota_client.py (add near top-level variables)
ROLE_PRESETS: Dict[str, set[int]] = {}  # NEW

SUPPORT_LEAN_TAGS = {"Support"}
OFFLANE_HEURISTIC_POSITIVE = {"Initiator", "Durable"}  # tweak as you like

def _build_role_presets():
    offlane_ids: set[int] = set()
    for hid, h in HEROES.items():
        roles = set(h.get("roles", []) or [])
        # Heuristic: Initiator/Durable often map to offlane cores.
        if roles & OFFLANE_HEURISTIC_POSITIVE and not (roles & SUPPORT_LEAN_TAGS):
            offlane_ids.add(hid)
    ROLE_PRESETS["offlane"] = offlane_ids

def ids_by_role_tags(required_any: set[str]) -> set[int]:
    """Return heroes that include ANY of the given Valve role tags."""
    out: set[int] = set()
    for hid, h in HEROES.items():
        roles = set(h.get("roles", []) or [])
        if roles & required_any:
            out.add(hid)
    return out

def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", s.lower())

async def _get_json(url: str):
    async with aiohttp.ClientSession() as s:
        async with s.get(url, timeout=20) as r:
            r.raise_for_status()
            return await r.json()

async def init_heroes():
    global HEROES, NAME_TO_ID, HERO_IMG
    data = await _get_json("https://api.opendota.com/api/heroStats")
    HEROES, NAME_TO_ID, HERO_IMG = {}, {}, {}
    for h in data:
        hid = h["id"]
        HEROES[hid] = h
        loc = h.get("localized_name") or ""
        raw = (h.get("name") or "").replace("npc_dota_hero_", "")
        for key in {loc, raw}:
            if key:
                NAME_TO_ID.setdefault(_norm(key), hid)
        if h.get("img"):
            HERO_IMG[hid] = f'{CDN}{h["img"]}'
    _build_role_presets()
async def hero_matchups(hero_id: int) -> List[dict]:
    # NEW: return if cached
    if hero_id in _MATCHUPS_CACHE:
        return _MATCHUPS_CACHE[hero_id]
    data = await _get_json(f"https://api.opendota.com/api/heroes/{hero_id}/matchups")
    _MATCHUPS_CACHE[hero_id] = data
    return data

def resolve_hero_ids(names: List[str]) -> List[int]:
    ids = []
    for n in names:
        k = _norm(n)
        if k in NAME_TO_ID:
            ids.append(NAME_TO_ID[k])
    return ids

async def counter_scores(
    enemy_ids: List[int],
    exclude_ids: List[int],
    include_only: Optional[set[int]] = None  # NEW (used by role filter in step 2)
) -> List[Tuple[int, float, int]]:
    results = []
    for cid, h in HEROES.items():
        if cid in exclude_ids:
            continue
        if include_only is not None and cid not in include_only:
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
