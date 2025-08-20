import re
from typing import Dict, List, Tuple, Optional, Set

def parse_role_param(
    text: str,
    role_presets: Dict[str, Set[int]],
    ids_by_role_tags_fn
) -> Tuple[Optional[Set[int]], str]:
    """
    Returns (include_only_ids, human_label) given a free-text that might contain role=...
    `ids_by_role_tags_fn(tags: set[str]) -> set[int]` is injected (from opendota_client).
    """
    m = re.search(r"\brole\s*=\s*([a-zA-Z, \-]+)", text)
    if not m:
        return None, ""
    raw = m.group(1).strip()
    key = raw.lower()
    if key in role_presets:
        return role_presets[key], f" (role={key})"
    tags = {t.strip() for t in raw.split(",") if t.strip()}
    if tags:
        return ids_by_role_tags_fn(tags), f" (roles any of: {', '.join(tags)})"
    return None, ""

def lock_in(board: Dict[str, List[int]], hero_id: int) -> Dict[str, List[int]]:
    """
    Pure function: returns an updated board with hero_id appended to 'my' if not present.
    Board shape: {"my": [ids...], "enemy": [ids...]}
    """
    new_board = {"my": list(board.get("my", [])), "enemy": list(board.get("enemy", []))}
    if hero_id not in new_board["my"]:
        new_board["my"].append(hero_id)
    return new_board
