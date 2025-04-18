import argparse
import json
import os
import torch


TAG_FILE = "resources/tags.json"
SYNONYM_FILE = "resources/tag_synonyms.json"


def ensure_tag_file():
    os.makedirs(os.path.dirname(TAG_FILE), exist_ok=True)
    if not os.path.exists(TAG_FILE):
        with open(TAG_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)
        print("ℹ️  Neue tags.json wurde erstellt.")

def load_tags(tag_file_path=TAG_FILE):
    ensure_tag_file()
    with open(tag_file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_tags(tags, tag_file_path=TAG_FILE):
    with open(tag_file_path, 'w', encoding='utf-8') as f:
        json.dump(tags, f, indent=2)

def load_synonyms():
    if os.path.exists(SYNONYM_FILE):
        with open(SYNONYM_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_synonyms(data):
    with open(SYNONYM_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Tag Verwaltung CLI")
    parser.add_argument("--add", type=str, help="Neuen Tag hinzufügen")
    parser.add_argument("--remove", type=str, help="Vorhandenen Tag entfernen")
    parser.add_argument("--list", action="store_true", help="Alle Tags anzeigen")
    parser.add_argument("--synonyms", action="store_true", help="Synonyme anzeigen")
    parser.add_argument("--reset-all", action="store_true", help="Löscht alle generierten Tag-Daten und erstellt alles neu")
    parser.add_argument("--workers", type=int, default=None, help="Anzahl paralleler Threads für rebuild")
    parser.add_argument("--dry-run", action="store_true", help="Nur anzeigen, was passieren würde, aber nichts ausführen")
    args = parser.parse_args()

    if args.reset_all:
        print("\n🔁 Starte vollständigen Reset ...")
        files_to_delete = [
            "resources/card_captions.json",
            "resources/card_tags.json",
            "resources/card_auto_tags.json",
            "resources/card_tags_merged.json"
        ]

        for file in files_to_delete:
            if os.path.exists(file):
                if args.dry_run:
                    print(f"📝 (dry-run) Würde löschen: {file}")
                else:
                    os.remove(file)
                    print(f"🗑️  Gelöscht: {file}")

        if args.dry_run:
            print("📝 (dry-run) Würde jetzt alle Karten neu verarbeiten...")
        else:
            from main import tag_all_parallel, update_tags_from_text_and_captions, export_json_for_frontend
            import gc

            try:
                tag_all_parallel(
                    "images",
                    "resources/scryfall-default-cards.json",
                    "resources/card_tags_merged.json",
                    max_workers=args.workers
                )
            finally:
                gc.collect()
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()

            update_tags_from_text_and_captions()
            export_json_for_frontend()
            print("✅ Neuaufbau abgeschlossen.")
        return

    if args.synonyms:
        print("\n🔗 Aktuelle Synonyme:")
        synonyms = load_synonyms()
        for base, alts in synonyms.items():
            print(f"- {base}: {', '.join(alts)}")
        return

    tags = load_tags()

    if args.add:
        if args.add not in tags:
            tags.append(args.add)
            save_tags(tags)
            print(f"✅ Tag '{args.add}' wurde hinzugefügt.")
        else:
            print(f"⚠️  Tag '{args.add}' existiert bereits.")

    if args.remove:
        if args.remove in tags:
            tags.remove(args.remove)
            save_tags(tags)
            print(f"🗑️ Tag '{args.remove}' wurde entfernt.")
        else:
            print(f"❌ Tag '{args.remove}' wurde nicht gefunden.")

    if args.list:
        print("\n📦 Aktuelle Tags:")
        for tag in tags:
            print(f"- {tag}")

if __name__ == "__main__":
    main()
