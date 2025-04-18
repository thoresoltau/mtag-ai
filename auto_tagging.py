import json
import os
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing

from auto_captioning import tag_image, generate_caption, process_card
from nlp_processing import extract_tags_from_text_fields
from tag_provider import TAGS, load_tags


def extract_tags_from_caption(caption, known_tags):
    caption_lower = caption.lower()
    return [tag for tag in known_tags if tag.lower() in caption_lower]


def auto_tag_from_captions(caption_path="resources/card_captions.json", output_path="resources/card_auto_tags.json"):
    with open(caption_path, 'r', encoding='utf-8') as f:
        captions = json.load(f)
    auto_tags = {}
    for card_id, caption in captions.items():
        auto_tags[card_id] = extract_tags_from_caption(caption, TAGS)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(auto_tags, f, indent=2)


def tag_all_images(img_dir, tag_output_path, merged_output_path, bulk_json_path):
    with open(bulk_json_path, 'r', encoding='utf-8') as f:
        cards = {card['id']: card for card in json.load(f)}

    existing = {}
    if os.path.exists(merged_output_path):
        with open(merged_output_path, 'r', encoding='utf-8') as f:
            existing = json.load(f)

    tagged_results = {}
    merged_results = existing.copy()

    for file in tqdm(os.listdir(img_dir)):
        if file.endswith(".jpg"):
            path = os.path.join(img_dir, file)
            card_id = file.replace(".jpg", "")
            if card_id in existing:
                continue
            tags = tag_image(path)
            caption = generate_caption(path)
            auto_tags = extract_tags_from_caption(caption, TAGS)
            card_data = cards.get(card_id, {})
            text_tags = extract_tags_from_text_fields(card_data)
            tagged_results[card_id] = tags
            merged_results[card_id] = {
                "name": card_data.get("name"),
                "colors": card_data.get("colors"),
                "type_line": card_data.get("type_line"),
                "oracle_text": card_data.get("oracle_text"),
                "legalities": card_data.get("legalities"),
                "image_url": card_data.get("image_uris", {}).get("normal"),
                "tags": tags,
                "auto_tags": auto_tags,
                "text_tags": text_tags,
                "caption": caption
            }

    with open(tag_output_path, 'w', encoding='utf-8') as f:
        json.dump(tagged_results, f, indent=2)

    with open(merged_output_path, 'w', encoding='utf-8') as f:
        json.dump(merged_results, f, indent=2)


def tag_all_parallel(img_dir, bulk_json_path, output_path="resources/card_tags_merged.json", max_workers=None):
    tags = load_tags()
    with open(bulk_json_path, 'r', encoding='utf-8') as f:
        card_db = {c['id']: c for c in json.load(f)}

    existing = {}
    if os.path.exists(output_path):
        with open(output_path, 'r', encoding='utf-8') as f:
            existing = json.load(f)

    img_files = [f for f in os.listdir(img_dir) if f.endswith(".jpg")]
    todo = [(f.replace(".jpg", ""), os.path.join(img_dir, f)) for f in img_files if f.replace(".jpg", "") not in existing]

    merged = existing.copy()
    if max_workers is None:
        max_workers = min(8, multiprocessing.cpu_count())

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_card, cid, path, card_db.get(cid, {}), tags) for cid, path in todo]
        for future in tqdm(as_completed(futures), total=len(futures), desc="🔍 Tagging"):
            cid, result = future.result()
            if result:
                merged[cid] = result

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(merged, f, indent=2)

    print(f"✅ {len(todo)} Karten verarbeitet und gespeichert (parallel mit {max_workers} Threads).")
