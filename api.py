# api.py
from fastapi import FastAPI, Query
from typing import List, Optional
import json

app = FastAPI()

with open("resources/card_tags_merged.json", "r", encoding="utf-8") as f:
    CARD_DATA = json.load(f)

@app.get("/search")
def search_cards(
        tags: Optional[List[str]] = Query(default=[]),
        colors: Optional[List[str]] = Query(default=[]),
        type_contains: Optional[str] = None,
        legal_in: Optional[str] = None
):
    results = []
    for card_id, card in CARD_DATA.items():
        if tags and not all(tag in card["tags"] for tag in tags):
            continue
        if colors and not (set(colors).intersection(set(card.get("colors") or []))):
            continue
        if type_contains and type_contains.lower() not in (card.get("type_line") or "").lower():
            continue
        if legal_in and (card.get("legalities") or {}).get(legal_in.lower()) != "legal":
            continue
        results.append(card)
    return results
