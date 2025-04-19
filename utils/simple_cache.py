# utils/simple_cache.py
import json, hashlib, os
from pathlib import Path

_CACHE_DIR = Path(".magic_cache")      # keep it local to the project root
_CACHE_DIR.mkdir(exist_ok=True)

def _key(book_name: str, book_text: str) -> Path:
    """
    Deterministic file name = slug(book_name) + 8‑char hash(book_text)
    """
    slug = "".join(c if c.isalnum() else "_" for c in book_name.lower())[:50]
    book_hash = hashlib.sha256(book_text.encode("utf-8")).hexdigest()[:8]
    return _CACHE_DIR / f"{slug}_{book_hash}.json"

def load(book_name: str, book_text: str):
    fp = _key(book_name, book_text)
    if fp.exists():
        try:
            return json.loads(fp.read_text())
        except Exception:
            fp.unlink(missing_ok=True)   # corrupted → ignore
    return None

def save(book_name: str, book_text: str, entities_map, relationships_map):
    fp = _key(book_name, book_text)
    fp.write_text(json.dumps(
        {"entities_map": entities_map, "relationships_map": relationships_map},
        ensure_ascii=False))
