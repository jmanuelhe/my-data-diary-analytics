"""Gráficos estáticos (matplotlib) y dashboard interactivo (Plotly)."""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

INK, CORAL, TEAL, GOLD, SLATE, SAND = "#1B2430", "#E4572E", "#17A398", "#F2A541", "#6B7A8F", "#F3EEE7"
PALETTE = [CORAL, TEAL, GOLD, "#3E6FB0", "#8E5BB5", SLATE]
MESES = {"2026-08": "Ago", "2026-09": "Sep", "2026-10": "Oct"}

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": SLATE, "axes.labelcolor": INK,
    "xtick.color": INK, "ytick.color": INK, "axes.spines.top": False, "axes.spines.right": False,
    "figure.facecolor": "white", "axes.facecolor": "white", "axes.titleweight": "bold", "axes.titlesize": 12,
})


def _save(fig, path: Path):
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def fig_format_mix(fmt_pct: pd.DataFrame, path: Path):
    fig, ax = plt.subplots(figsize=(8, 3.6))
    left = pd.Series(0.0, index=fmt_pct.index)
    labels = [MESES.get(m, m) for m in fmt_pct.index]
    for col, color in zip(fmt_pct.columns, PALETTE):
        ax.barh(labels, fmt_pct[col], left=left, color=color, label=col, height=0.6)
        for i, (v, l) in enumerate(zip(fmt_pct[col], left)):
            if v >= 8:
                ax.text(l + v / 2, i, f"{v:.0f}%", ha="center", va="center", color="white", fontsize=9, fontweight="bold")
        left += fmt_pct[col]
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xlabel("% de publicaciones del mes")
    ax.set_title("¿Qué tipo de contenido publica el canal cada mes?", loc="left")
    ax.legend(ncol=3, frameon=False, bbox_to_anchor=(0, -0.25), loc="upper left", fontsize=9)
    _save(fig, path)


def fig_topic_heatmap(topic_pct: pd.DataFrame, path: Path):
    t = topic_pct.drop(index="IA general", errors="ignore")
    t = t.loc[t.mean(axis=1).sort_values(ascending=False).index]
    fig, ax = plt.subplots(figsize=(6.5, 4.6))
    im = ax.imshow(t.values, cmap="YlOrRd", aspect="auto", vmin=0)
    ax.set_xticks(range(t.shape[1]), [MESES.get(c, c) for c in t.columns])
    ax.set_yticks(range(t.shape[0]), t.index)
    for i in range(t.shape[0]):
        for j in range(t.shape[1]):
            v = t.values[i, j]
            ax.text(j, i, f"{v:.0f}%", ha="center", va="center", fontsize=9,
                    color="white" if v > t.values.max() * 0.6 else INK)
    ax.set_title("Temas: % de publicaciones del mes que los mencionan", loc="left")
    ax.spines[:].set_visible(False)
    fig.colorbar(im, ax=ax, shrink=0.8, label="%")
    _save(fig, path)


def fig_timeline(df: pd.DataFrame, path: Path):
    daily = df.groupby("fecha").size().reindex(
        pd.date_range(df["fecha"].min(), df["fecha"].max()), fill_value=0)
    weekly = daily.resample("W-SUN").agg(["sum", "size"])  # size = días del rango que caen en esa semana
    full = weekly["size"] == 7
    fig, ax = plt.subplots(figsize=(8, 3.2))
    ax.bar(weekly.index, weekly["sum"], width=5, color=[TEAL if f else "#BFD9D6" for f in full])
    mean_full = weekly.loc[full, "sum"].mean()
    ax.axhline(mean_full, color=CORAL, ls="--", lw=1.2)
    ax.text(weekly.index[1], mean_full + 0.3, f"promedio {mean_full:.1f}/semana (solo semanas completas)",
            color=CORAL, fontsize=9)
    ax.text(1, -0.22, "Barras claras = semanas incompletas al inicio/fin del periodo", transform=ax.transAxes,
            ha="right", fontsize=8, color=SLATE)
    ax.set_ylabel("publicaciones")
    ax.set_title("Publicaciones por semana", loc="left")
    _save(fig, path)


def fig_weekday(s: pd.Series, path: Path):
    fig, ax = plt.subplots(figsize=(6, 3))
    colors = [CORAL if v == s.max() else SLATE for v in s.values]
    ax.bar(s.index, s.values, color=colors)
    for i, v in enumerate(s.values):
        ax.text(i, v + 0.2, str(v), ha="center", fontsize=9)
    ax.set_title("Publicaciones por día de la semana", loc="left")
    _save(fig, path)


def dashboard(df: pd.DataFrame, fmt_pct: pd.DataFrame, topic_pct: pd.DataFrame, k: dict, path: Path):
    """Dashboard HTML autocontenido (Plotly vía CDN) para explorar los datos."""
    meses = [MESES.get(m, m) for m in fmt_pct.index]
    fig = make_subplots(rows=2, cols=2, subplot_titles=(
        "Formato por mes (%)", "Temas por mes (%)", "Publicaciones por día", "Publicaciones por formato"),
        specs=[[{"type": "bar"}, {"type": "heatmap"}], [{"type": "scatter"}, {"type": "pie"}]],
        vertical_spacing=0.16)
    for col, color in zip(fmt_pct.columns, PALETTE):
        fig.add_trace(go.Bar(name=col, x=meses, y=fmt_pct[col], marker_color=color, legendgroup="f"), 1, 1)
    t = topic_pct.drop(index="IA general", errors="ignore")
    fig.add_trace(go.Heatmap(z=t.values, x=[MESES.get(c, c) for c in t.columns], y=t.index,
                             colorscale="YlOrRd", showscale=False,
                             hovertemplate="%{y} · %{x}: %{z:.0f}%<extra></extra>"), 1, 2)
    daily = df.groupby("fecha").agg(n=("titulo", "size"), titulos=("titulo", lambda x: "<br>".join(x)))
    fig.add_trace(go.Scatter(x=daily.index, y=daily["n"], mode="markers+lines", line=dict(color=TEAL),
                             text=daily["titulos"], hovertemplate="%{x|%d %b}<br>%{text}<extra></extra>",
                             showlegend=False), 2, 1)
    fc = df["formato"].value_counts()
    fig.add_trace(go.Pie(labels=fc.index, values=fc.values, hole=0.55, marker=dict(colors=PALETTE),
                         showlegend=False, textinfo="percent"), 2, 2)
    fig.update_layout(barmode="stack", height=820, template="simple_white",
                      title=dict(text=f"My Data Diary · {k['periodo']} · {k['total_publicaciones']} publicaciones",
                                 x=0.01), font=dict(family="Inter, Arial", color=INK),
                      legend=dict(orientation="h", y=1.08))
    table = df[["fecha", "titulo", "formato", "temas", "link"]].copy()
    table["fecha"] = table["fecha"].dt.strftime("%Y-%m-%d")
    table["temas"] = table["temas"].map(", ".join)
    table["titulo"] = [f'<a href="{l}" target="_blank">{t}</a>' if l else t for t, l in zip(table.titulo, table.link)]
    rows = "".join(f"<tr><td>{r.fecha}</td><td>{r.titulo}</td><td>{r.formato}</td><td>{r.temas}</td></tr>"
                   for r in table.itertuples())
    kpi_html = "".join(f'<div class="k"><b>{v}</b><span>{lbl}</span></div>' for lbl, v in [
        ("publicaciones", k["total_publicaciones"]), ("días con post", k["dias_con_publicacion"]),
        ("constancia", f'{k["constancia_pct"]}%'), ("posts/semana", k["posts_por_semana"])])
    html = f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>My Data Diary · Dashboard</title>
<style>body{{font-family:Inter,Arial,sans-serif;color:{INK};margin:0;background:{SAND}}}
main{{max-width:1150px;margin:auto;padding:24px 16px}}.ks{{display:flex;gap:12px;flex-wrap:wrap}}
.k{{background:#fff;border-radius:10px;padding:14px 18px;flex:1;min-width:140px}}.k b{{font-size:28px;display:block;color:{CORAL}}}
.card{{background:#fff;border-radius:10px;padding:8px;margin-top:16px;overflow-x:auto}}table{{border-collapse:collapse;width:100%;font-size:14px}}
td,th{{padding:6px 8px;border-bottom:1px solid #eee;text-align:left;vertical-align:top}}a{{color:{TEAL}}}
input{{padding:8px;width:100%;box-sizing:border-box;border:1px solid #ccc;border-radius:6px;margin-bottom:8px}}</style>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script></head><body><main>
<h1>My Data Diary · análisis de contenido</h1><div class="ks">{kpi_html}</div>
<div class="card">{fig.to_html(full_html=False, include_plotlyjs=False)}</div>
<div class="card"><h2>Todas las publicaciones</h2><input id="q" placeholder="Filtrar por título, formato o tema…">
<table id="t"><thead><tr><th>Fecha</th><th>Título</th><th>Formato</th><th>Temas</th></tr></thead><tbody>{rows}</tbody></table></div>
</main><script>document.getElementById('q').addEventListener('input',e=>{{const q=e.target.value.toLowerCase();
document.querySelectorAll('#t tbody tr').forEach(r=>r.style.display=r.innerText.toLowerCase().includes(q)?'':'none')}})</script>
</body></html>"""
    path.write_text(html, encoding="utf-8")
