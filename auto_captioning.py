import os
from PIL import Image
from transformers import CLIPProcessor, CLIPModel, BlipProcessor, BlipForConditionalGeneration
import json
import torch
import gc

from nlp_processing import extract_tags_from_text_fields
from tag_provider import TAGS

# Setup: download and init models
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

device = "cuda" if torch.cuda.is_available() else "cpu"
clip_model.to(device)
blip_model.to(device)

# Function to tag images using CLIP
def tag_image(img_path, tags=TAGS):
    image = Image.open(img_path).convert("RGB")
    inputs = clip_processor(text=tags, images=image, return_tensors="pt", padding=True)
    outputs = clip_model(**inputs)
    logits_per_image = outputs.logits_per_image[0]
    probs = logits_per_image.softmax(dim=0)
    scored_tags = [(tag, float(probs[i])) for i, tag in enumerate(tags)]
    return [tag for tag, score in scored_tags if score > 0.15]

# Function to generate captions for images using BLIP
def generate_caption(img_path):
    image = Image.open(img_path).convert("RGB")
    inputs = blip_processor(images=image, return_tensors="pt")
    out = blip_model.generate(
        **inputs,
        max_new_tokens=100,
        num_beams=5,
        do_sample=True,
        top_k=50,
        top_p=0.95,
        repetition_penalty=1.2
    )
    caption = blip_processor.decode(out[0], skip_special_tokens=True)
    return caption

# Function to caption all images in a directory
def caption_all_images(img_dir, output_path="resources/card_captions.json"):
    existing = {}
    if os.path.exists(output_path):
        with open(output_path, 'r', encoding='utf-8') as f:
            existing = json.load(f)

    results = existing.copy()
    for file in os.listdir(img_dir):
        if file.endswith(".jpg"):
            path = os.path.join(img_dir, file)
            card_id = file.replace(".jpg", "")
            if card_id in existing:
                continue
            try:
                caption = generate_caption(path)
                results[card_id] = caption
            except Exception as e:
                print(f"Fehler bei {file}: {e}")

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)


def process_card(card_id, path, card_data, tags):
    try:
        with Image.open(path) as img:
            image = img.convert("RGB")

        clip_inputs = clip_processor(text=tags, images=image, return_tensors="pt", padding=True)
        for k in clip_inputs:
            clip_inputs[k] = clip_inputs[k].to(device)
        clip_outputs = clip_model(**clip_inputs)
        probs = clip_outputs.logits_per_image[0].softmax(dim=0)
        scored_tags = [(tag, float(probs[i])) for i, tag in enumerate(tags)]
        tag_result = [tag for tag, score in scored_tags if score > 0.15]

        blip_inputs = blip_processor(images=image, return_tensors="pt").to(device)
        out = blip_model.generate(
            **blip_inputs,
            max_new_tokens=100,
            num_beams=5,
            do_sample=True,
            top_k=50,
            top_p=0.95,
            repetition_penalty=1.2
        )
        caption = blip_processor.decode(out[0], skip_special_tokens=True)

        auto_tags = [t for t in tags if t.lower() in caption.lower()]
        text_tags = extract_tags_from_text_fields(card_data)

        del image, clip_inputs, clip_outputs, blip_inputs, out
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        return card_id, {
            "name": card_data.get("name"),
            "colors": card_data.get("colors"),
            "type_line": card_data.get("type_line"),
            "oracle_text": card_data.get("oracle_text"),
            "legalities": card_data.get("legalities"),
            "image_url": card_data.get("image_uris", {}).get("normal"),
            "tags": tag_result,
            "auto_tags": auto_tags,
            "text_tags": text_tags,
            "caption": caption
        }
    except Exception as e:
        print(f"❌ Fehler bei {card_id}: {e}")
        return card_id, None

