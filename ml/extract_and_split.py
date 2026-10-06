import os
import zipfile
import json
import random
from collections import Counter

print("==================================================")
print("PHASE 6: EXTRACTING & SPLITTING DISEASE DATASET")
print("==================================================")

zip_path = r"C:\Users\sagar\Downloads\archive (2).zip"
extract_dir = r"c:\Users\sagar\OneDrive\Desktop\farm_sathii\ml\datasets\crop_diseases"
split_manifest_path = r"c:\Users\sagar\OneDrive\Desktop\farm_sathii\ml\datasets\dataset_split.json"

if not os.path.exists(zip_path):
    raise FileNotFoundError(f"Source archive not found at: {zip_path}")

os.makedirs(extract_dir, exist_ok=True)

# 1. Extract zip if not already extracted
existing_files = []
for root, dirs, files in os.walk(extract_dir):
    for f in files:
        if f.lower().endswith(('.jpg', '.jpeg', '.png')):
            existing_files.append(os.path.join(root, f))

if len(existing_files) == 13324:
    print(f"Dataset already fully extracted ({len(existing_files)} images found). Skipping extraction.")
else:
    print(f"Extracting {zip_path} to {extract_dir} ...")
    with zipfile.ZipFile(zip_path, 'r') as z:
        # Extract files under Crop Diseases
        members = [m for m in z.namelist() if not m.endswith('/') and m.lower().endswith(('.jpg', '.jpeg', '.png'))]
        print(f"Total archive members to extract: {len(members)}")
        z.extractall(extract_dir)
    print("Extraction complete.")

# 2. Discover all extracted images and group by class
print("\nDiscovering extracted classes and images...")
class_to_images = {}
for root, dirs, files in os.walk(extract_dir):
    for f in files:
        if f.lower().endswith(('.jpg', '.jpeg', '.png')):
            rel_path = os.path.relpath(os.path.join(root, f), extract_dir)
            parts = rel_path.replace('\\', '/').split('/')
            # Expected structure: Crop Diseases/<class_name>/<filename> or <class_name>/<filename>
            if len(parts) >= 2:
                cls_name = parts[-2]
                class_to_images.setdefault(cls_name, []).append(rel_path.replace('\\', '/'))

print(f"Discovered {len(class_to_images)} classes:")
total_images = sum(len(imgs) for imgs in class_to_images.values())
print(f"Total valid image paths: {total_images}")

sorted_classes = sorted(list(class_to_images.keys()))
class_to_idx = {cls: idx for idx, cls in enumerate(sorted_classes)}

# 3. Create reproducible Stratified Split (70% Train, 15% Val, 15% Test, seed=42)
random.seed(42)

split_data = {
    "classes": sorted_classes,
    "class_to_idx": class_to_idx,
    "total_images": total_images,
    "splits": {
        "train": [],
        "val": [],
        "test": []
    },
    "counts": {
        "train": {},
        "val": {},
        "test": {}
    }
}

for cls in sorted_classes:
    imgs = sorted(class_to_images[cls]) # sort for determinism
    random.shuffle(imgs)
    
    n_total = len(imgs)
    n_train = int(0.70 * n_total)
    n_val = int(0.15 * n_total)
    # Remaining goes to test to account for rounding
    train_imgs = imgs[:n_train]
    val_imgs = imgs[n_train:n_train + n_val]
    test_imgs = imgs[n_train + n_val:]
    
    split_data["counts"]["train"][cls] = len(train_imgs)
    split_data["counts"]["val"][cls] = len(val_imgs)
    split_data["counts"]["test"][cls] = len(test_imgs)
    
    for img_rel in train_imgs:
        split_data["splits"]["train"].append({"path": img_rel, "class": cls, "label": class_to_idx[cls]})
    for img_rel in val_imgs:
        split_data["splits"]["val"].append({"path": img_rel, "class": cls, "label": class_to_idx[cls]})
    for img_rel in test_imgs:
        split_data["splits"]["test"].append({"path": img_rel, "class": cls, "label": class_to_idx[cls]})

# Save split manifest
with open(split_manifest_path, "w", encoding="utf-8") as f:
    json.dump(split_data, f, indent=2)

print("\n--- STRATIFIED SPLIT SUMMARY ---")
print(f"Train samples: {len(split_data['splits']['train'])} ({len(split_data['splits']['train'])/total_images*100:.1f}%)")
print(f"Val samples:   {len(split_data['splits']['val'])} ({len(split_data['splits']['val'])/total_images*100:.1f}%)")
print(f"Test samples:  {len(split_data['splits']['test'])} ({len(split_data['splits']['test'])/total_images*100:.1f}%)")
print(f"Manifest written to: {split_manifest_path}")

print("\nPer-class split breakdown:")
print(f"{'Class Name':<32} {'Total':<6} {'Train':<6} {'Val':<6} {'Test':<6}")
print("-" * 58)
for cls in sorted_classes:
    tot = len(class_to_images[cls])
    tr = split_data["counts"]["train"][cls]
    v = split_data["counts"]["val"][cls]
    te = split_data["counts"]["test"][cls]
    print(f"{cls:<32} {tot:<6} {tr:<6} {v:<6} {te:<6}")

print("\nDataset extraction and reproducible split completed successfully!")
