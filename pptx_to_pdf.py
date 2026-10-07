import shutil
import subprocess
import sys
from pathlib import Path

SOFFICE_CANDIDATES = [
    "soffice",
    "libreoffice",
    "/Applications/LibreOffice.app/Contents/MacOS/soffice",
]


def find_soffice() -> str:
    for candidate in SOFFICE_CANDIDATES:
        path = shutil.which(candidate) or (candidate if Path(candidate).exists() else None)
        if path:
            return path
    raise FileNotFoundError("LibreOffice не найден. Установи: brew install --cask libreoffice")


def pptx_to_pdf(src: Path, out_dir: Path | None = None) -> Path:
    src = src.resolve()
    out_dir = (out_dir or src.parent).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [find_soffice(), "--headless", "--convert-to", "pdf", "--outdir", str(out_dir), str(src)],
        check=True,
        capture_output=True,
    )
    return out_dir / f"{src.stem}.pdf"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Использование: python pptx_to_pdf.py file.pptx|папка [папка_вывода]")

    target = Path(sys.argv[1])
    out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    files = sorted(target.glob("*.pptx")) if target.is_dir() else [target]

    for f in files:
        print(f"Готово: {pptx_to_pdf(f, out_dir)}")
