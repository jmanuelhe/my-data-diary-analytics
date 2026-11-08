import pandas as pd

from src.mdd.clean import clean_posts, normalize_title


def _raw(rows):
    return pd.DataFrame(rows, columns=["fecha", "titulo", "resumen", "link", "informe"])


def test_normalize_title_strips_reshare_mark():
    assert normalize_title("Create a ChatGPT  (reenviado)") == "create a chatgpt"


def test_reshare_detected_by_mark_and_by_repeated_link():
    df = clean_posts(_raw([
        ("2026-08-02", "A post", "", "https://x/a", "agosto"),
        ("2026-08-30", "A post (reenviado)", "", "https://x/a", "agosto"),
        ("2026-09-10", "A post", "", "https://x/a", "septiembre"),
    ]))
    assert df["es_reenvio"].tolist() == [False, True, True]


def test_recurring_series_is_not_a_reshare():
    df = clean_posts(_raw([
        ("2026-08-27", "AI Engineer Jobs", "", "https://x/aug", "agosto"),
        ("2026-09-24", "AI Engineer Jobs", "", "https://x/sep", "septiembre"),
    ]))
    assert not df["es_reenvio"].any()


def test_exact_duplicates_removed_and_sorted():
    df = clean_posts(_raw([
        ("2026-09-01", "B", "", "", "s"), ("2026-08-01", "A", "", "", "a"), ("2026-08-01", "A", "", "", "a"),
    ]))
    assert df["titulo"].tolist() == ["A", "B"]
