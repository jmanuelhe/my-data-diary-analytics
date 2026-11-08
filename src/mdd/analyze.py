"""Métricas e indicadores del canal."""
from __future__ import annotations

import pandas as pd

from .classify import explode_topics


def kpis(df: pd.DataFrame) -> dict:
    original = df[~df["es_reenvio"]]
    start, end = df["fecha"].min(), df["fecha"].max()
    span_days = (end - start).days + 1
    active_days = df["fecha"].nunique()
    return {
        "total_publicaciones": int(len(df)),
        "publicaciones_originales": int(len(original)),
        "reenvios": int(df["es_reenvio"].sum()),
        "periodo": f"{start.date()} → {end.date()}",
        "dias_del_periodo": int(span_days),
        "dias_con_publicacion": int(active_days),
        "constancia_pct": round(100 * active_days / span_days, 1),
        "posts_por_semana": round(len(df) / (span_days / 7), 2),
        "dias_con_mas_de_un_post": int((df.groupby("fecha").size() > 1).sum()),
        "pct_con_link": round(100 * df["tiene_link"].mean(), 1),
    }


def monthly_counts(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("mes").agg(publicaciones=("titulo", "size"),
                                 dias_activos=("fecha", "nunique")).reset_index()


def format_by_month(df: pd.DataFrame, normalize: bool = True) -> pd.DataFrame:
    t = pd.crosstab(df["mes"], df["formato"], normalize="index" if normalize else False)
    return (t * 100).round(1) if normalize else t


def topic_by_month(df: pd.DataFrame) -> pd.DataFrame:
    """% de publicaciones del mes que tocan cada tema (un post puede tocar varios)."""
    e = explode_topics(df)
    counts = pd.crosstab(e["tema"], e["mes"])
    per_month = df.groupby("mes").size()
    return (counts.div(per_month, axis=1) * 100).round(1)


def topic_shift(df: pd.DataFrame) -> pd.DataFrame:
    """Cambio en puntos porcentuales entre el primer y el último mes."""
    t = topic_by_month(df)
    first, last = t.columns[0], t.columns[-1]
    out = pd.DataFrame({"primer_mes": t[first], "ultimo_mes": t[last]})
    out["cambio_pp"] = (out["ultimo_mes"] - out["primer_mes"]).round(1)
    return out.sort_values("cambio_pp", ascending=False)


def weekday_counts(df: pd.DataFrame) -> pd.Series:
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    es = dict(zip(order, ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]))
    s = df["dia_semana"].value_counts().reindex(order, fill_value=0)
    s.index = [es[d] for d in s.index]
    return s


def gaps(df: pd.DataFrame) -> pd.DataFrame:
    """Rachas sin publicar (días consecutivos sin ningún post)."""
    days = pd.Series(sorted(df["fecha"].unique()))
    diffs = days.diff().dt.days.fillna(1).astype(int)
    rows = [{"desde": (days[i - 1] + pd.Timedelta(days=1)).date(),
             "hasta": (days[i] - pd.Timedelta(days=1)).date(),
             "dias_sin_post": int(diffs[i] - 1)}
            for i in range(1, len(days)) if diffs[i] > 1]
    return pd.DataFrame(rows).sort_values("dias_sin_post", ascending=False) if rows else pd.DataFrame(
        columns=["desde", "hasta", "dias_sin_post"])
