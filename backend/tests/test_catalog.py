from app.catalog import load_packs


def test_all_category_packs_load():
    packs = load_packs()
    expected = {
        "entertainment",
        "everyday_life",
        "fun_and_games",
        "the_world",
        "variety",
        "sports",
        "food_and_drink",
        "science_and_tech",
        "animals",
        "places",
        "music",
    }
    assert expected <= set(packs)
    for pack in packs.values():
        assert len(pack.phrases) >= 40
        assert len(set(pack.phrases)) == len(pack.phrases)
