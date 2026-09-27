from types import SimpleNamespace
from app.services.matching import token_similarity, metadata_score, final_score

def test_token_similarity():
    assert token_similarity("black backpack orange zipper", "dark backpack orange zip") > 0.2

def test_metadata_category_and_color():
    a = SimpleNamespace(category="backpack", color="black", latitude=28.6, longitude=77.3, location_name="Library", event_time=None)
    b = SimpleNamespace(category="backpack", color="black", latitude=28.6, longitude=77.3, location_name="Cafeteria", event_time=None)
    attr, loc, tim = metadata_score(a, b)
    assert attr == 1.0
    assert loc > 0.9

def test_score_is_bounded():
    s = final_score(1, 1, 1, 1, 1)
    assert 0 <= s <= 1
