#!/usr/bin/env python3
"""Create a SQLite database indexing files in the repository."""

import argparse
import sqlite3
from pathlib import Path


EXCLUDED_DIRS = {".git", "node_modules", "__pycache__", ".venv"}


def should_skip(path: Path) -> bool:
    return any(part in EXCLUDED_DIRS for part in path.parts)


def index_files(root: Path, db_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS files (
            path TEXT PRIMARY KEY,
            mtime REAL,
            content BLOB
        )
        """
    )
    for file_path in root.rglob("*"):
        if file_path.is_file() and not should_skip(file_path):
            cur.execute(
                "INSERT OR REPLACE INTO files (path, mtime, content) VALUES (?, ?, ?)",
                (
                    str(file_path.relative_to(root)),
                    file_path.stat().st_mtime,
                    file_path.read_bytes(),
                ),
            )
    conn.commit()
    conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a SQLite DB of project files")
    parser.add_argument("--root", default=".", help="Project root directory")
    parser.add_argument(
        "--db", default="project_files.db", help="Path to the SQLite database"
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    db_path = Path(args.db).resolve()
    index_files(root, db_path)


if __name__ == "__main__":
    main()
