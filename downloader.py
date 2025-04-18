import os
import requests
from tqdm import tqdm
import json


def download_card_images(bulk_json_path, output_dir, limit=100):
    os.makedirs(output_dir, exist_ok=True)
    with open(bulk_json_path, 'r', encoding='utf-8') as f:
        cards = json.load(f)

    existing_ids = {filename.replace(".jpg", "") for filename in os.listdir(output_dir) if filename.endswith(".jpg")}
    count = 0

    for card in tqdm(cards):
        card_id = card['id']
        if card_id in existing_ids:
            continue

        if 'image_uris' in card and card['image_uris'].get('normal'):
            img_url = card['image_uris']['normal']
            img_name = f"{card_id}.jpg"
            img_path = os.path.join(output_dir, img_name)

            try:
                img_data = requests.get(img_url).content
                with open(img_path, 'wb') as f:
                    f.write(img_data)
            except Exception as e:
                print(f"Fehler bei {card['name']}: {e}")

            count += 1
            if count >= limit:
                break

    print(f"📥 {count} neue Bilder heruntergeladen.")
