import argparse
from auto_tagging import tag_all_images, tag_all_parallel
from downloader import download_card_images
from nlp_processing import update_tags_from_text_and_captions
from ui_exporter import export_json_for_frontend


# 1. Bilder herunterladen
# download_card_images("default-cards.json", "images", limit=100)

# 2. Beispiel: Tagging eines Bildes
#download_card_images("resources/scryfall-default-cards.json", "images", limit=1000)
#tag_all_images("images", "resources/card_tags.json", "resources/card_tags_merged.json", "resources/scryfall-default-cards.json")
#caption_all_images("images")
#auto_tag_from_captions()
#suggest_tags_from_captions()
#export_json_for_frontend()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Magic Card Tagger")
    parser.add_argument("--images", type=str, default="images", help="Pfad zum Bildordner")
    parser.add_argument("--bulk", type=str, default="resources/scryfall-default-cards.json", help="Pfad zur Scryfall JSON")
    parser.add_argument("--output", type=str, default="resources/card_tags_merged.json", help="Ausgabepfad der Tag-Datenbank")
    parser.add_argument("--workers", type=int, default=None, help="Anzahl der parallelen Threads")
    parser.add_argument("--download", action="store_true", help="Bilder herunterladen")
    parser.add_argument("--limit", type=int, default=100, help="Maximale Anzahl neuer Bilder")
    args = parser.parse_args()

    if args.download:
        download_card_images(args.bulk, args.images, limit=args.limit)

    tag_all_parallel(args.images, args.bulk, args.output, max_workers=args.workers)
    update_tags_from_text_and_captions(args.output)
    export_json_for_frontend()