#!/usr/bin/env python3
"""Create the employee-facing homework ZIP and its SHA-256 checksum."""

from hashlib import sha256
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[1]
PACK_NAME = "EVERYONE-ELSE-AI-HUMAN-HOMEWORK-PACK"
OUTPUT = ROOT / f"{PACK_NAME}.zip"
HASH_FILE = ROOT / f"{PACK_NAME}.sha256"

TOP_FILES = [
    "START-HERE.md",
    "COPY-PASTE-PROMPTS.txt",
    "EVERYONE-ELSE-AI-HUMAN-HOMEWORK-GUIDE.pdf",
    "EVERYONE-ELSE-AI-HUMAN-HOMEWORK-GUIDE.docx",
    "EVERYONE-ELSE-AI-HUMAN-HOMEWORK-VIDEO.mp4",
    "EVERYONE-ELSE-AI-HUMAN-HOMEWORK-VIDEO-TRANSCRIPT.txt",
    "EVERYONE-ELSE-AI-HUMAN-HOMEWORK-VIDEO-CAPTIONS.srt",
    "EVERYONE-ELSE-AI-HUMAN-HOMEWORK-VIDEO-SCRIPT.md",
    "SOURCE-MANIFEST.md",
    "VET-REPORT.md",
]


def add_file(archive: ZipFile, path: Path) -> None:
    relative = path.relative_to(ROOT)
    info = ZipInfo(f"{PACK_NAME}/{relative.as_posix()}", date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    archive.writestr(info, path.read_bytes())


def build() -> None:
    missing = [name for name in TOP_FILES if not (ROOT / name).is_file()]
    if missing:
        raise SystemExit("Missing release files: " + ", ".join(missing))

    with ZipFile(OUTPUT, "w", compression=ZIP_DEFLATED, compresslevel=6) as archive:
        for name in TOP_FILES:
            add_file(archive, ROOT / name)
        for path in sorted((ROOT / "AI-HUMAN-STARTERS").rglob("*")):
            if path.is_file():
                add_file(archive, path)

    digest = sha256(OUTPUT.read_bytes()).hexdigest()
    HASH_FILE.write_text(f"{digest}  {OUTPUT.name}\n", encoding="utf-8")
    print(OUTPUT)
    print(HASH_FILE)
    print(digest)


if __name__ == "__main__":
    build()
