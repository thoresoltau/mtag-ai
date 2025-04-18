import json


# Load tags from external file
def load_tags(tag_file_path="resources/tags.json"):
    with open(tag_file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

## Save tags to external file
def save_tags(tags, tag_file_path="resources/tags.json"):
    with open(tag_file_path, 'w', encoding='utf-8') as f:
        json.dump(tags, f, indent=2)

TAGS = load_tags()
