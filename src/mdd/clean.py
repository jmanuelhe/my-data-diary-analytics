"""Limpieza y normalización del dataset de publicaciones."""
from __future__ import annotations

import re

import pandas as pd

RESHARE_PATTERN = re.compile(r"\s*\((?:reenviado|reshared?)\)\s*$", re.IGNORECASE)


def normalize_title(title: str) -> str:
    """Quita marcas de reenvío, espacios repetidos y pasa a minúsculas (clave de comparación)."""
    t = RESHARE_PATTERN.sub("", title)
    t = re.sub(r"\s+", " ", t).strip().lower()
    return t


def clean_posts(raw: pd.DataFrame) -> pd.DataFrame:
    """Devuelve un DataFrame limpio con columnas derivadas.

    Reglas:
    - `fecha` se convierte a datetime y se ordena cronológicamente.
    - `es_reenvio`: True si el título trae la marca "(reenviado)" o si el mismo
      contenido (título normalizado + link) ya había aparecido antes.
    - Títulos iguales con fechas distintas y links distintos NO son duplicados:
      son series recurrentes (p. ej. la lista mensual de empleos).
    - Se eliminan duplicados exactos (misma fecha y mismo título).
    """
    df = raw.copy()
    df["fecha"] = pd.to_datetime(df["fecha"], format="%Y-%m-%d")
    df["titulo"] = df["titulo"].str.strip()
    df["link"] = df["link"].fillna("").str.strip()
    df = df.drop_duplicates(subset=["fecha", "titulo"]).sort_values("fecha", kind="stable")

    df["titulo_norm"] = df["titulo"].map(normalize_title)
    marked = df["titulo"].str.contains(RESHARE_PATTERN)
    key = df["titulo_norm"] + "|" + df["link"]
    repeated_same_link = key.duplicated() & (df["link"] != "")
    df["es_reenvio"] = marked | repeated_same_link

    df["mes"] = df["fecha"].dt.to_period("M").astype(str)
    df["dia_semana"] = df["fecha"].dt.day_name()
    df["semana_iso"] = df["fecha"].dt.isocalendar().week.astype(int)
    df["tiene_link"] = df["link"] != ""
    return df.reset_index(drop=True)
