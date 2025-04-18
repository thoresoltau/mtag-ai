import os
import json
import spacy

from tag_provider import load_tags, save_tags

nlp = spacy.load("en_core_web_sm")
STOPWORDS = set(spacy.lang.en.stop_words.STOP_WORDS)

# update tags.json with new tags from text and captions
def update_tags_from_text_and_captions(merged_path="resources/card_tags_merged.json", tag_path="resources/tags.json"):
    tags = set()

    if os.path.exists(tag_path):
        tags.update(load_tags(tag_path))

    if not os.path.exists(merged_path):
        return

    with open(merged_path, 'r', encoding='utf-8') as f:
        cards = json.load(f)

    for card in cards.values():
        for group in ["tags", "auto_tags", "text_tags"]:
            for tag in card.get(group, []):
                tag = tag.strip().lower()
                if tag and len(tag) > 1:
                    tags.add(tag)

    tags = sorted(tags)
    save_tags(tags, tag_path)
    print("✅ tags.json automatisch aktualisiert (mit Duplikat-Filter).")

    print("🧠 baue Synonym-Mapping auf...")
    synonyms = build_synonym_map(tags)
    with open("resources/tag_synonyms.json", "w", encoding="utf-8") as f:
        json.dump(synonyms, f, indent=2)
    print("🔁 Synonyme gespeichert in tag_synonyms.json")

    print("🔄 Normalisiere tags.json anhand Synonymgruppen...")
    normalized_tags = normalize_tags_with_synonyms(tags, synonyms)
    save_tags(normalized_tags, tag_path)
    print("✨ Normalisierte Tags gespeichert.")

# normalize the tags based on the synonym map
def normalize_tags_with_synonyms(tags, synonym_map):
    normalized = set()
    for tag in tags:
        found = False
        for main_tag, synonyms in synonym_map.items():
            if tag == main_tag or tag in synonyms:
                normalized.add(main_tag)
                found = True
                break
        if not found:
            normalized.add(tag)
    return list(sorted(normalized))

# extract keywords from flavor text
def extract_keywords_from_flavor(flavor_text):
    doc = nlp(flavor_text)
    keywords = set()
    for chunk in doc.noun_chunks:
        text = chunk.text.strip().lower()
        if len(text) > 1 and text not in STOPWORDS:
            keywords.add(text)
    return list(keywords)

# extract tags from text fields
def extract_tags_from_text_fields(card, known_tags=None):
    words = set()
    type_line = card.get("type_line", "").lower().replace("—", " ").replace("-", " ")
    for word in type_line.split():
        if len(word) > 1 and word not in STOPWORDS:
            words.add(word)
    flavor = card.get("flavor_text", "").strip()
    words.update(extract_keywords_from_flavor(flavor))
    return list(words)

# build a synonym map based on similarity
def build_synonym_map(tags, threshold=0.8):
    seen = set()
    synonym_groups = []
    vectors = {tag: nlp(tag) for tag in tags if nlp(tag).has_vector}
    for tag, doc in vectors.items():
        if tag in seen:
            continue
        group = set()
        for other_tag, other_doc in vectors.items():
            if other_tag in seen or tag == other_tag:
                continue
            if doc.similarity(other_doc) > threshold:
                group.add(other_tag)
        if group:
            group.add(tag)
            seen.update(group)
            synonym_groups.append(sorted(group))
    # Umwandlung in Mapping: jeweils erstes Wort als Key
    return {group[0]: group[1:] for group in synonym_groups if len(group) > 1}
