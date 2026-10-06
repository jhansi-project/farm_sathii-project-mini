import os
import json
import time
from pathlib import Path
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, models
from PIL import Image
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
)

class DiseaseEvalDataset(Dataset):
    def __init__(self, items, base_dir, transform=None):
        self.items = items
        self.base_dir = base_dir
        self.transform = transform

    def __len__(self):
        return len(self.items)

    def __getitem__(self, idx):
        item = self.items[idx]
        img_path = self.base_dir / item["path"]
        image = Image.open(img_path).convert("RGB")
        if self.transform:
            image = self.transform(image)
        return image, item["label"]

def evaluate():
    print("=== EVALUATING SAVED MOBILENETV3-LARGE CHECKPOINT ===")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if device.type == "cpu":
        torch.set_num_threads(8)

    base_dir = Path("ml/datasets/crop_diseases")
    split_path = Path("ml/datasets/dataset_split.json")
    model_path = Path("ml/models/farmsathi_disease_model.pth")
    metrics_path = Path("ml/models/disease_eval_metrics.json")

    with open(split_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    classes = manifest["classes"]
    num_classes = len(classes)
    test_items = manifest["splits"]["test"]
    print(f"Test samples: {len(test_items)} across {num_classes} classes.")

    eval_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])

    test_dataset = DiseaseEvalDataset(test_items, base_dir, eval_transform)
    test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False, num_workers=0)

    # Reconstruct architecture
    model = models.mobilenet_v3_large(weights=None)
    model.classifier[3] = nn.Sequential(
        nn.Dropout(p=0.3),
        nn.Linear(in_features=1280, out_features=num_classes)
    )

    state_dict = torch.load(model_path, map_location=device)
    model.load_state_dict(state_dict)
    model = model.to(device)
    model.eval()

    model_size_bytes = os.path.getsize(model_path)
    model_size_mb = model_size_bytes / (1024 * 1024)

    test_preds = []
    test_labels = []
    latencies = []

    print("Running inference on held-out test set...")
    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(device)
            t0 = time.perf_counter()
            outputs = model(images)
            batch_latency = (time.perf_counter() - t0) / images.size(0)
            latencies.append(batch_latency)

            _, preds = torch.max(outputs, 1)
            test_preds.extend(preds.cpu().numpy())
            test_labels.extend(labels.numpy())

    acc = accuracy_score(test_labels, test_preds)
    macro_prec = precision_score(test_labels, test_preds, average="macro", zero_division=0)
    macro_rec = recall_score(test_labels, test_preds, average="macro", zero_division=0)
    macro_f1 = f1_score(test_labels, test_preds, average="macro", zero_division=0)
    weighted_f1 = f1_score(test_labels, test_preds, average="weighted", zero_division=0)

    avg_latency_ms = (sum(latencies) / len(latencies)) * 1000

    print("\n==================================================")
    print("ACTUAL TEST EVALUATION METRICS (HELD-OUT TEST SET)")
    print("==================================================")
    print(f"Total Test Images: {len(test_labels)}")
    print(f"Accuracy:          {acc*100:.2f}% ({acc:.4f})")
    print(f"Macro Precision:   {macro_prec*100:.2f}% ({macro_prec:.4f})")
    print(f"Macro Recall:      {macro_rec*100:.2f}% ({macro_rec:.4f})")
    print(f"Macro F1-Score:    {macro_f1*100:.2f}% ({macro_f1:.4f})")
    print(f"Weighted F1-Score: {weighted_f1*100:.2f}% ({weighted_f1:.4f})")
    print(f"Measured Model Size:             {model_size_mb:.2f} MB ({model_size_bytes} bytes)")
    print(f"Measured Per-Image Inference Latency: {avg_latency_ms:.2f} ms")

    report_str = classification_report(test_labels, test_preds, target_names=classes, digits=4, zero_division=0)
    report_dict = classification_report(test_labels, test_preds, target_names=classes, output_dict=True, zero_division=0)
    cm = confusion_matrix(test_labels, test_preds).tolist()

    print("\n--- Detailed Per-Class Classification Report ---")
    print(report_str)

    # Save metrics JSON
    metrics_data = {
        "architecture": "MobileNetV3-Large",
        "num_classes": num_classes,
        "classes": classes,
        "test_samples": len(test_labels),
        "measured_metrics": {
            "accuracy": round(float(acc), 4),
            "macro_precision": round(float(macro_prec), 4),
            "macro_recall": round(float(macro_rec), 4),
            "macro_f1": round(float(macro_f1), 4),
            "weighted_f1": round(float(weighted_f1), 4),
            "model_size_mb": round(float(model_size_mb), 2),
            "inference_latency_ms": round(float(avg_latency_ms), 2),
        },
        "per_class_report": report_dict,
        "confusion_matrix": cm,
    }

    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics_data, f, indent=2)
    print(f"\nSaved evaluation metrics to: {metrics_path}")

if __name__ == "__main__":
    evaluate()
