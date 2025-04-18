import os
import shutil


def export_json_for_frontend():
    target_path = os.path.join("magic-card-ui", "public", "resources")
    os.makedirs(target_path, exist_ok=True)
    for file in os.listdir("resources"):
        if file.endswith(".json"):
            shutil.copyfile(os.path.join("resources", file), os.path.join(target_path, file))
    print("📦 JSON-Dateien ins Frontend exportiert.")
