# tests/test_opendota_client.py
import asyncio
import importlib
import types
import pytest

@pytest.mark.asyncio
async def test_init_heroes_builds_maps(monkeypatch, sample_hero_stats):
    from tools import opendota_client as oc

    async def fake_get_json(url: str):
        assert "heroStats" in url
        return sample_hero_stats

    # reset module state
    oc.HEROES.clear()
    oc.NAME_TO_ID.clear()
    oc.HERO_IMG.clear()
    oc.ROLE_PRESETS.clear()

    monkeypatch.setattr(oc, "_get_json", fake_get_json)
    await oc.init_heroes()

    # basic assertions
    assert len(oc.HEROES) == 4
    assert oc.NAME_TO_ID["antimage"] == 1
    assert oc.NAME_TO_ID["pudge"] == 2
    assert oc.HERO_IMG[1].startswith("https://cdn.cloudflare.steamstatic.com")

    # role presets are built
    assert "offlane" in oc.ROLE_PRESETS
    # Axe should be in offlane heuristic (Initiator/Durable)
    assert 4 in oc.ROLE_PRESETS["offlane"]

@pytest.mark.asyncio
async def test_hero_matchups_is_cached(monkeypatch, sample_hero_stats, sample_matchups):
    from tools import opendota_client as oc

    calls = {"n": 0}

    async def fake_get_json(url: str):
        if "heroStats" in url:
            return sample_hero_stats
        # /heroes/{id}/matchups
        calls["n"] += 1
        hid = int(url.split("/heroes/")[1].split("/")[0])
        return sample_matchups[hid]

    oc.HEROES.clear(); oc.NAME_TO_ID.clear(); oc.HERO_IMG.clear(); oc.ROLE_PRESETS.clear()
    oc._MATCHUPS_CACHE.clear()
    monkeypatch.setattr(oc, "_get_json", fake_get_json)

    await oc.init_heroes()

    # first call should hit network
    m1 = await oc.hero_matchups(4)
    # second call should be cache
    m2 = await oc.hero_matchups(4)

    assert m1 == m2
    assert calls["n"] == 1, "Expected one network hit due to caching"

@pytest.mark.asyncio
async def test_counter_scores_and_include_only(monkeypatch, sample_hero_stats, sample_matchups):
    from tools import opendota_client as oc
    import math

    async def fake_get_json(url: str):
        if "heroStats" in url:
            return sample_hero_stats
        hid = int(url.split("/heroes/")[1].split("/")[0])
        return sample_matchups[hid]

    oc.HEROES.clear(); oc.NAME_TO_ID.clear(); oc.HERO_IMG.clear(); oc.ROLE_PRESETS.clear()
    oc._MATCHUPS_CACHE.clear()
    monkeypatch.setattr(oc, "_get_json", fake_get_json)
    await oc.init_heroes()

    # Enemies: Pudge (2), Storm (3)
    enemy_ids = [2, 3]
    exclude_ids = enemy_ids[:]  # don’t recommend already-present

    # No include_only: Axe should rank above Anti-Mage
    results = await oc.counter_scores(enemy_ids, exclude_ids, include_only=None)
    top_ids = [hid for (hid, _, _) in results[:2]]
    assert 4 in top_ids, "Axe should appear as a strong counter"
    assert top_ids.index(4) < top_ids.index(1), "Axe should outrank Anti-Mage"

    # include_only limited to {1}: only Anti-Mage can appear
    limited = await oc.counter_scores(enemy_ids, exclude_ids, include_only={1})
    assert all(hid == 1 for (hid, _, _) in limited), "Only Anti-Mage should be in results when include_only={1}"
