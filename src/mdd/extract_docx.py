"""Extrae la tabla de cronología de los informes .docx a un CSV.

Uso: python -m src.mdd.extract_docx carpeta_con_informes data/raw/posts_raw.csv
Los .docx originales no se incluyen en el repo; el CSV resultante sí.
"""
import csv
import sys
from pathlib import Path

import docx

MONTHS = {"ago": 8, "sep": 9, "oct": 10}
REL_ID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"


def extract(folder: Path) -> list[dict]:
    rows = []
    for path in sorted(folder.glob("informe_my_data_diary_*.docx")):
        d = docx.Document(path)
        informe = path.stem.rsplit("_", 1)[-1]
        for table in d.tables:
            for r in table.rows[1:]:  # la fila 0 es el encabezado
                fecha, titulo, resumen = (c.text.strip() for c in r.cells[:3])
                link = ""
                for h in r._tr.xpath(".//w:hyperlink"):
                    rid = h.get(REL_ID)
                    if rid in d.part.rels:
                        link = d.part.rels[rid].target_ref
                day, mon = fecha.split()
                rows.append({"fecha": f"2026-{MONTHS[mon]:02d}-{int(day):02d}", "titulo": titulo,
                             "resumen": resumen, "link": link, "informe": informe})
    return rows


if __name__ == "__main__":
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    rows = extract(src)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} filas → {out}")
