"""Ejecuta el pipeline completo: limpiar → clasificar → analizar → graficar → reportar."""
import json
from pathlib import Path

import pandas as pd

from src.mdd import analyze, viz
from src.mdd.classify import add_labels
from src.mdd.clean import clean_posts

ROOT = Path(__file__).parent
FIG = ROOT / "reports" / "figures"


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    raw = pd.read_csv(ROOT / "data/raw/posts_raw.csv")
    df = add_labels(clean_posts(raw))
    out = df.assign(temas=df["temas"].map("; ".join))
    out.to_csv(ROOT / "data/processed/posts_clean.csv", index=False)

    k = analyze.kpis(df)
    fmt = analyze.format_by_month(df)
    topics = analyze.topic_by_month(df)
    shift = analyze.topic_shift(df)
    wd = analyze.weekday_counts(df)
    g = analyze.gaps(df)

    viz.fig_format_mix(fmt, FIG / "formato_por_mes.png")
    viz.fig_topic_heatmap(topics, FIG / "temas_por_mes.png")
    viz.fig_timeline(df, FIG / "publicaciones_por_semana.png")
    viz.fig_weekday(wd, FIG / "dia_semana.png")
    viz.dashboard(df, fmt, topics, k, ROOT / "reports" / "dashboard.html")

    results = {"kpis": k, "mensual": analyze.monthly_counts(df).to_dict("records"),
               "formato_pct": fmt.to_dict(), "cambio_temas_pp": shift["cambio_pp"].to_dict(),
               "dia_semana": wd.to_dict(), "rachas_sin_post": g.head(5).astype(str).to_dict("records")}
    (ROOT / "reports" / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
