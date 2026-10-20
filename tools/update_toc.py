"""Расставляет якоря у нумерованных заголовков ноутбука и пересобирает оглавление.

Формат как в ноутбуках преподавателя (расширение VSCode «Jupyter TOC»):
    ### 1.2.1. <a id='toc1_2_1_'></a>[Название](#toc0_)

Использование: python tools/update_toc.py [warcraft.ipynb]
"""
import json
import re
import sys
from pathlib import Path

HEADING = re.compile(r"^(#{1,6}) (\d+(?:\.\d+)*)\.? (?:<a id='toc[\d_]+'></a>\[)?(.+?)(?:\]\(#toc0_\))?\s*$")
TOC_MARKER = "<a id='toc0_'></a>"
TOC_CONFIG = """<!-- vscode-jupyter-toc-config
	numbering=true
	anchor=true
	flat=false
	minLevel=1
	maxLevel=6
	/vscode-jupyter-toc-config -->
<!-- THIS CELL WILL BE REPLACED ON TOC UPDATE. DO NOT WRITE YOUR TEXT IN THIS CELL -->"""


def anchor(number: str) -> str:
    return "toc" + "".join(f"{part}_" for part in number.split("."))


def main(path: Path) -> None:
    nb = json.loads(path.read_text(encoding="utf-8"))
    toc_cell = None
    entries = []

    for cell in nb["cells"]:
        if cell["cell_type"] != "markdown":
            continue
        text = "".join(cell["source"])
        if TOC_MARKER in text:
            toc_cell = cell
            continue
        lines = text.split("\n")
        for i, line in enumerate(lines):
            m = HEADING.match(line)
            if not m:
                continue
            hashes, number, title = m.groups()
            aid = anchor(number)
            lines[i] = f"{hashes} {number}. <a id='{aid}'></a>[{title}](#toc0_)"
            entries.append("  " * (len(hashes) - 1) + f"- {number}. [{title}](#{aid})    ")
        cell["source"] = "\n".join(lines).splitlines(keepends=True)

    if toc_cell is None:
        sys.exit(f"В {path} нет ячейки оглавления с {TOC_MARKER}")
    toc = f"**Table of contents**{TOC_MARKER}    \n" + "\n".join(entries) + "\n\n" + TOC_CONFIG
    toc_cell["source"] = toc.splitlines(keepends=True)

    path.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{path}: {len(entries)} пунктов в оглавлении")


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else "warcraft.ipynb"))
