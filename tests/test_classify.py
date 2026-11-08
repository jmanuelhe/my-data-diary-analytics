"""Valida las reglas contra un conjunto etiquetado a mano (ground truth)."""
import pytest

from src.mdd.classify import classify_format, classify_topics

GOLD = [
    ("Remote AI/ML Internships for October", "Empleo y pasantías"),
    ("AI Agents Are Changing AI Jobs", "Opinión y tendencias"),
    ("Build a Multi-Agent Web Scraper with CrewAI", "Proyecto guiado"),
    ("How I Built a Computer-Use AI Agent with Python", "Proyecto guiado"),
    ("15 AI Agent Projects to Build in 2026", "Banco de proyectos"),
    ("Multi-Agent Projects I'd Build to Stand Out in AI Engineer Interviews", "Banco de proyectos"),
    ("How to Survive a Live Machine Learning Coding Interview", "Entrevistas y práctica"),
    ("5 NumPy Problems Every ML Engineer Should Solve", "Entrevistas y práctica"),
    ("MLOps for AI Engineers Roadmap", "Rutas y conceptos"),
    ("AI Skills You Should Learn Before Applying for Internships", "Rutas y conceptos"),
    ("How I Use LLMs as a Thinking Partner Every Day", "Opinión y tendencias"),
]


@pytest.mark.parametrize("title,expected", GOLD)
def test_format(title, expected):
    assert classify_format(title) == expected


def test_topics_multilabel():
    t = classify_topics("Build an LLM Cost & Latency Tracker with Python")
    assert set(t) == {"LLMs y GenAI", "MLOps y producción", "Python y datos"}


def test_topics_empty_when_generic():
    assert classify_topics("50 Real-World AI Projects for 2026") == []


def test_mcp_not_matched_inside_words():
    assert "MCP" not in classify_topics("Something about mcpherson")
