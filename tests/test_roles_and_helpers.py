# tests/test_roles_and_helpers.py
from app_helpers import parse_role_param, lock_in

def test_parse_role_param_preset():
    role_presets = {"offlane": {4, 5, 6}}
    def fake_ids_by_role_tags(tags):  # not used in this case
        return set()
    include_only, label = parse_role_param(
        "counterpicks: pudge, storm spirit role=offlane",
        role_presets,
        fake_ids_by_role_tags
    )
    assert include_only == {4, 5, 6}
    assert "(role=offlane)" in label

def test_parse_role_param_raw_tags():
    role_presets = {}
    def fake_ids_by_role_tags(tags):
        assert tags == {"Initiator", "Durable"}
        return {4, 7}
    include_only, label = parse_role_param(
        "counterpicks: pudge, storm spirit role=Initiator,Durable",
        role_presets,
        fake_ids_by_role_tags
    )
    assert include_only == {4, 7}
    assert "roles any of" in label

def test_parse_role_param_absent():
    include_only, label = parse_role_param(
        "counterpicks: pudge, storm spirit",
        {},
        lambda tags: set()
    )
    assert include_only is None and label == ""

def test_lock_in_helper_adds_once():
    board = {"my": [1], "enemy": [2]}
    updated = lock_in(board, 4)
    assert updated["my"] == [1, 4]
    # duplicate should not re-add
    updated2 = lock_in(updated, 4)
    assert updated2["my"] == [1, 4]
