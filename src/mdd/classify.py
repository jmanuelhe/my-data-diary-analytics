"""Clasificación por reglas: formato (una etiqueta) y temas (multi-etiqueta).

Se usan reglas con expresiones regulares en lugar de un modelo porque:
1. El dataset es pequeño (~80 filas): no alcanza para entrenar un clasificador.
2. Las reglas son auditables: cualquiera puede ver por qué un post cayó en una categoría.
3. Se validan con un conjunto etiquetado a mano (tests/test_classify.py).
"""
from __future__ import annotations

import re

import pandas as pd

# El orden importa: gana la primera regla que coincide.
FORMAT_RULES: list[tuple[str, str]] = [
    # Piezas de opinión que mencionan empleo/entrevistas pero no son ofertas ni guías.
    ("Opinión y tendencias", r"(are changing|what happens|matter less|thinking partner|career paths|should you still|can make mistakes)"),
    ("Rutas y conceptos", r"skills you (should|need to) learn"),
    ("Empleo y pasantías", r"\b(internships?|jobs?|hiring)\b"),
    ("Proyecto guiado", r"^(build|building|create|creating|how i built|i built|i deployed|"
                        r"how to build|setting up|how i set up|how i connect|add an llm|how to evaluate)\b"),
    ("Banco de proyectos", r"\bprojects?\b"),
    ("Entrevistas y práctica", r"\b(interviews?|questions|problems)\b"),
    ("Rutas y conceptos", r"\b(roadmap|resources|courses|framework|stack|concepts|cheat sheet|study|book|patterns|tools to learn|skills)\b"),
]
DEFAULT_FORMAT = "Opinión y tendencias"

TOPIC_RULES: dict[str, str] = {
    "Agentes de IA": r"\b(agents?|agentic|crewai|langgraph|computer-use|code assistant|ai data analyst)\b",
    "Multi-agente": r"\bmulti-agent\b",
    "RAG y documentos": r"\b(rag|documents?|q&a|own data|any website)\b",
    "LLMs y GenAI": r"\b(llms?|genai|chatgpt|fine-tuning)\b",
    "MLOps y producción": r"\b(mlops|pipeline|monitoring|retrains?|ci/cd|evals?|evaluate|latency|deployed)\b",
    "Visión y multimodal": r"\b(vision|multimodal|on-device)\b",
    "MCP": r"\bmcp\b",
    "Carrera profesional": r"\b(jobs?|internships?|interviews?|career|hiring|resume|skills)\b",
    "Python y datos": r"\b(python|pandas|numpy|sql|csv)\b",
}


def classify_format(title: str) -> str:
    t = title.lower()
    for label, pattern in FORMAT_RULES:
        if re.search(pattern, t):
            return label
    return DEFAULT_FORMAT


def classify_topics(title: str) -> list[str]:
    t = title.lower()
    return [label for label, pattern in TOPIC_RULES.items() if re.search(pattern, t)]


def add_labels(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["formato"] = out["titulo"].map(classify_format)
    out["temas"] = out["titulo"].map(classify_topics)
    out["n_temas"] = out["temas"].map(len)
    return out


def explode_topics(df: pd.DataFrame) -> pd.DataFrame:
    """Una fila por (post, tema). Los posts sin tema quedan como 'IA general'."""
    e = df.assign(tema=df["temas"].map(lambda ts: ts or ["IA general"])).explode("tema")
    return e.reset_index(drop=True)
