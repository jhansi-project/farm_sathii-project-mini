# pyright: reportMissingImports=false
import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple

# PyTorch deep learning framework
import torch  # type: ignore
import torch.nn as nn  # type: ignore
from torch.utils.data import Dataset, DataLoader  # type: ignore
from torchvision import transforms, models  # type: ignore
from PIL import Image
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
)

# ----------------------------------------------------
# 1. Dataset Implementation
# ----------------------------------------------------
class DiseaseDataset(Dataset):
    def __init__(self, items: List[Dict], base_dir: Path, transform=None):
        self.items = items
        self.base_dir = base_dir
        self.transform = transform

    def __len__(self):
        return len(self.items)

    def __getitem__(self, idx):
        item = self.items[idx]
        img_path = self.base_dir / item["path"]
        image = Image.open(img_path).convert("RGB")
        label = item["label"]

        if self.transform:
            image = self.transform(image)

        return image, label


# ----------------------------------------------------
# 2. Main Training & Evaluation Pipeline
# ----------------------------------------------------
def run_pipeline():
    print("==================================================")
    print("PHASE 6: MOBILENETV3-LARGE DISEASE MODEL TRAINING")
    print("==================================================")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Execution Device: {device}")
    if device.type == "cpu":
        torch.set_num_threads(8)
        print(f"Configured PyTorch CPU threads: {torch.get_num_threads()}")

    # Paths
    base_dir = Path("ml/datasets/crop_diseases")
    split_manifest_path = Path("ml/datasets/dataset_split.json")
    model_save_dir = Path("ml/models")
    model_save_dir.mkdir(parents=True, exist_ok=True)

    model_save_path = model_save_dir / "farmsathi_disease_model.pth"
    classes_save_path = model_save_dir / "disease_classes.json"
    metrics_save_path = model_save_dir / "disease_eval_metrics.json"

    # Load split manifest
    with open(split_manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    classes = manifest["classes"]
    class_to_idx = manifest["class_to_idx"]
    num_classes = len(classes)
    print(f"Number of classes: {num_classes}")

    # Save class list artifact
    with open(classes_save_path, "w", encoding="utf-8") as f:
        json.dump({"classes": classes, "class_to_idx": class_to_idx}, f, indent=2)
    print(f"Saved class mapping artifact to: {classes_save_path}")

    # Transforms
    train_transform = transforms.Compose([
        transforms.RandomResizedCrop(224, scale=(0.8, 1.0)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.5),
        transforms.RandomRotation(degrees=15),
        transforms.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])

    eval_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])

    # Datasets & Loaders
    train_dataset = DiseaseDataset(manifest["splits"]["train"], base_dir, train_transform)
    val_dataset = DiseaseDataset(manifest["splits"]["val"], base_dir, eval_transform)
    test_dataset = DiseaseDataset(manifest["splits"]["test"], base_dir, eval_transform)

    batch_size = 32 if torch.cuda.is_available() else 32
    num_workers = 0  # Safe for Windows multi-threading

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=num_workers)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers)

    print(f"Train samples: {len(train_dataset)} ({len(train_loader)} batches)")
    print(f"Val samples:   {len(val_dataset)} ({len(val_loader)} batches)")
    print(f"Test samples:  {len(test_dataset)} ({len(test_loader)} batches)")

    # Compute Class-Imbalance Weights
    train_counts = [manifest["counts"]["train"][c] for c in classes]
    total_train = sum(train_counts)
    class_weights = [total_train / (num_classes * count) for count in train_counts]
    class_weights_tensor = torch.tensor(class_weights, dtype=torch.float).to(device)
    class_weights_tensor = class_weights_tensor / class_weights_tensor.mean()
    print("Class imbalance weights calculated to reduce majority-class bias and improve minority-class recall.")

    # Model Architecture
    print("\nLoading MobileNetV3-Large with pretrained ImageNet weights...")
    model = models.mobilenet_v3_large(weights=models.MobileNet_V3_Large_Weights.DEFAULT)

    # Modify Classifier Head
    # MobileNetV3 classifier: [0]=Linear(960, 1280), [1]=Hardswish(), [2]=Dropout(0.2), [3]=Linear(1280, 1000)
    model.classifier[3] = nn.Sequential(
        nn.Dropout(p=0.3),
        nn.Linear(in_features=1280, out_features=num_classes)
    )
    model = model.to(device)

    # Loss, Optimizer & Scheduler
    criterion = nn.CrossEntropyLoss(weight=class_weights_tensor)

    backbone_params = [p for name, p in model.named_parameters() if not name.startswith("classifier.3")]
    head_params = [p for name, p in model.named_parameters() if name.startswith("classifier.3")]

    optimizer = torch.optim.AdamW([
        {"params": backbone_params, "lr": 1e-4},
        {"params": head_params, "lr": 1e-3},
    ], weight_decay=1e-2)

    epochs = 10
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-6)

    # Training Loop
    best_val_f1 = 0.0
    best_epoch = 0
    patience = 3
    patience_counter = 0

    print(f"\n--- Starting Training for {epochs} Epochs ---")
    start_train_time = time.time()

    for epoch in range(1, epochs + 1):
        epoch_start = time.time()
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0

        for batch_idx, (images, labels) in enumerate(train_loader, start=1):
            images = images.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * images.size(0)
            _, preds = torch.max(outputs, 1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)

            if batch_idx % 50 == 0 or batch_idx == len(train_loader):
                batch_acc = (preds == labels).sum().item() / labels.size(0)
                print(f"  [Epoch {epoch:02d}/{epochs:02d}] Batch {batch_idx:03d}/{len(train_loader):03d} - Loss: {loss.item():.4f}, Batch Acc: {batch_acc*100:.1f}%")

        scheduler.step()
        train_loss = running_loss / total
        train_acc = correct / total

        # Validation
        model.eval()
        val_running_loss = 0.0
        val_preds_list = []
        val_labels_list = []

        with torch.no_grad():
            for images, labels in val_loader:
                images = images.to(device)
                labels = labels.to(device)

                outputs = model(images)
                loss = criterion(outputs, labels)

                val_running_loss += loss.item() * images.size(0)
                _, preds = torch.max(outputs, 1)
                val_preds_list.extend(preds.cpu().numpy())
                val_labels_list.extend(labels.cpu().numpy())

        val_loss = val_running_loss / len(val_dataset)
        val_acc = accuracy_score(val_labels_list, val_preds_list)
        val_f1 = f1_score(val_labels_list, val_preds_list, average="macro", zero_division=0)
        epoch_time = time.time() - epoch_start

        print(
            f"Epoch [{epoch:02d}/{epochs:02d}] ({epoch_time:.1f}s) - "
            f"Train Loss: {train_loss:.4f} Acc: {train_acc*100:.2f}% | "
            f"Val Loss: {val_loss:.4f} Acc: {val_acc*100:.2f}% Macro-F1: {val_f1*100:.2f}%"
        )

        # Checkpoint based on validation Macro-F1
        if val_f1 > best_val_f1:
            best_val_f1 = val_f1
            best_epoch = epoch
            patience_counter = 0
            torch.save(model.state_dict(), model_save_path)
            print(f"  --> Saved new best model checkpoint (Val Macro-F1: {val_f1*100:.2f}%)")
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"Early stopping triggered after {epoch} epochs (no improvement for {patience} epochs).")
                break

    total_train_duration = time.time() - start_train_time
    print(f"\nTraining completed in {total_train_duration/60:.2f} minutes.")
    print(f"Best validation Macro-F1: {best_val_f1*100:.2f}% at epoch {best_epoch}")

    # ----------------------------------------------------
    # 3. Final Evaluation on Held-Out Test Set (2,010 images)
    # ----------------------------------------------------
    print("\n--- Evaluating Best Model on Held-Out Test Set ---")
    model.load_state_dict(torch.load(model_save_path, map_location=device))
    model.eval()

    test_preds_list = []
    test_labels_list = []
    test_probs_list = []
    latencies = []

    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(device)
            labels = labels.to(device)

            t0 = time.perf_counter()
            outputs = model(images)
            latencies.append((time.perf_counter() - t0) / images.size(0))

            probs = torch.softmax(outputs, dim=1)
            _, preds = torch.max(outputs, 1)

            test_preds_list.extend(preds.cpu().numpy())
            test_labels_list.extend(labels.cpu().numpy())
            test_probs_list.extend(probs.cpu().numpy())

    # Calculate actual metrics
    test_acc = accuracy_score(test_labels_list, test_preds_list)
    macro_precision = precision_score(test_labels_list, test_preds_list, average="macro", zero_division=0)
    macro_recall = recall_score(test_labels_list, test_preds_list, average="macro", zero_division=0)
    macro_f1 = f1_score(test_labels_list, test_preds_list, average="macro", zero_division=0)

    weighted_precision = precision_score(test_labels_list, test_preds_list, average="weighted", zero_division=0)
    weighted_recall = recall_score(test_labels_list, test_preds_list, average="weighted", zero_division=0)
    weighted_f1 = f1_score(test_labels_list, test_preds_list, average="weighted", zero_division=0)

    clf_report_dict = classification_report(
        test_labels_list, test_preds_list, target_names=classes, output_dict=True, zero_division=0
    )
    clf_report_str = classification_report(
        test_labels_list, test_preds_list, target_names=classes, digits=4, zero_division=0
    )
    cm = confusion_matrix(test_labels_list, test_preds_list).tolist()

    # Actual measurements
    model_size_bytes = os.path.getsize(model_save_path)
    model_size_mb = model_size_bytes / (1024 * 1024)
    avg_inference_latency_ms = (sum(latencies) / len(latencies)) * 1000

    print(f"\n==================================================")
    print(f"ACTUAL MEASURED TEST RESULTS (HELD-OUT TEST SET)")
    print(f"==================================================")
    print(f"Total Test Images: {len(test_labels_list)}")
    print(f"Accuracy:          {test_acc*100:.2f}% ({test_acc:.4f})")
    print(f"Macro Precision:   {macro_precision*100:.2f}% ({macro_precision:.4f})")
    print(f"Macro Recall:      {macro_recall*100:.2f}% ({macro_recall:.4f})")
    print(f"Macro F1-Score:    {macro_f1*100:.2f}% ({macro_f1:.4f})")
    print(f"Weighted F1-Score: {weighted_f1*100:.2f}% ({weighted_f1:.4f})")
    print(f"\nMeasured Model Size:             {model_size_mb:.2f} MB ({model_size_bytes} bytes)")
    print(f"Measured Per-Image Inference Latency: {avg_inference_latency_ms:.2f} ms")

    print("\n--- Detailed Classification Report ---")
    print(clf_report_str)

    # Save complete evaluation metrics JSON
    metrics_data = {
        "architecture": "MobileNetV3-Large",
        "num_classes": num_classes,
        "classes": classes,
        "test_samples": len(test_labels_list),
        "measured_metrics": {
            "accuracy": round(float(test_acc), 4),
            "macro_precision": round(float(macro_precision), 4),
            "macro_recall": round(float(macro_recall), 4),
            "macro_f1": round(float(macro_f1), 4),
            "weighted_precision": round(float(weighted_precision), 4),
            "weighted_recall": round(float(weighted_recall), 4),
            "weighted_f1": round(float(weighted_f1), 4),
            "model_size_mb": round(float(model_size_mb), 2),
            "inference_latency_ms": round(float(avg_inference_latency_ms), 2),
        },
        "per_class_report": clf_report_dict,
        "confusion_matrix": cm,
    }

    with open(metrics_save_path, "w", encoding="utf-8") as f:
        json.dump(metrics_data, f, indent=2)

    print(f"\nSaved metrics report to: {metrics_save_path}")
    print("==================================================")
    print("PHASE 6 MODEL TRAINING & EVALUATION COMPLETE")
    print("==================================================")


if __name__ == "__main__":
    run_pipeline()
