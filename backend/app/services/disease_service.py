import io
import json
import logging
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import uuid

from fastapi import HTTPException, status
from PIL import Image
import numpy as np
import torch
import torch.nn as nn
from torchvision import models, transforms
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.disease_diagnosis import DiseaseDiagnosis
from app.models.user import User
from app.schemas.disease import (
    DiseaseDiagnosisResponse,
    DiseaseModelMetricsResponse,
    ManagementGuidance,
    TopDiseasePrediction,
)
from app.services.storage_service import storage_service

logger = logging.getLogger("farmsathi.disease_service")


CULTURAL_MANAGEMENT_KNOWLEDGE: Dict[str, Dict[str, Any]] = {
    "Corn___Common_Rust": {
        "cultural_practices": [
            "Plant rust-resistant or tolerant corn hybrids recommended for your region.",
            "Monitor fields during cool, humid weather when dew periods exceed 6 hours.",
            "Maintain balanced nitrogen levels; avoid excessive nitrogen fertilization.",
        ],
        "sanitation": [
            "Incorporate or till crop debris post-harvest to reduce overwintering teliospores.",
            "Practice crop rotation with non-host crops such as soybeans or legumes.",
        ],
        "prevention": [
            "Plant early in the season to avoid peak spore dispersal periods.",
            "Ensure adequate plant spacing to facilitate air circulation and canopy drying.",
        ],
        "disclaimer": "This guidance covers agronomic and cultural practices. Consult your local agricultural extension service or Krishi Vigyan Kendra (KVK) for regional chemical spray advisories.",
    },
    "Corn___Gray_Leaf_Spot": {
        "cultural_practices": [
            "Select corn hybrids with certified resistance to Gray Leaf Spot.",
            "Adopt crop rotation with non-grass crops for at least 1-2 years.",
            "Reduce planting density slightly to improve air movement through the canopy.",
        ],
        "sanitation": [
            "Bury infected crop residues through conservation tillage where appropriate.",
            "Remove volunteer corn plants around field perimeters.",
        ],
        "prevention": [
            "Avoid overhead irrigation during late afternoon or evening to minimize leaf wetness duration.",
            "Apply balanced potassium to strengthen plant epidermal cell walls.",
        ],
        "disclaimer": "This guidance covers agronomic and cultural practices. Consult your local agricultural extension service or Krishi Vigyan Kendra (KVK) for regional chemical spray advisories.",
    },
    "Corn___Healthy": {
        "cultural_practices": [
            "Continue standard agronomic practices and maintain recommended nutrient management.",
            "Ensure regular scout monitoring for early signs of leaf discoloration or pest activity.",
        ],
        "sanitation": [
            "Keep field borders free from weeds that may harbor insect vectors or fungal spores.",
        ],
        "prevention": [
            "Maintain optimal soil moisture and balanced N-P-K fertilization according to soil health card.",
        ],
        "disclaimer": "Your corn crop foliage appears healthy with no visible foliar disease symptoms detected.",
    },
    "Corn___Northern_Leaf_Blight": {
        "cultural_practices": [
            "Choose resistant hybrids with Ht-gene resistance.",
            "Practice minimum two-year crop rotation out of corn in heavily infested fields.",
            "Avoid continuous corn cropping in fields with past blight history.",
        ],
        "sanitation": [
            "Incorporate stubble and leaf residue thoroughly into the soil post-harvest to accelerate decomposition.",
        ],
        "prevention": [
            "Space rows adequately to accelerate leaf drying after rain or heavy morning dew.",
            "Perform periodic scouting starting from the lower canopy during pre-tasseling stage.",
        ],
        "disclaimer": "This guidance covers agronomic and cultural practices. Consult your local agricultural extension service or Krishi Vigyan Kendra (KVK) for regional chemical spray advisories.",
    },
    "Potato___Early_Blight": {
        "cultural_practices": [
            "Use certified, disease-free seed tubers.",
            "Implement 2-3 year crop rotation with non-solanaceous crops (e.g., cereals or pulses).",
            "Maintain plant vigor through balanced fertilization; stressed plants are more susceptible.",
        ],
        "sanitation": [
            "Destroy diseased foliage and cull piles promptly; avoid leaving them near potato fields.",
            "Avoid damaging tubers during harvesting and handling.",
        ],
        "prevention": [
            "Use drip irrigation instead of overhead sprinklers to prevent prolonged leaf wetness.",
            "Harvest only when vines are completely dead and tuber skin has set.",
        ],
        "disclaimer": "This guidance covers agronomic and cultural practices. Consult your local agricultural extension service or Krishi Vigyan Kendra (KVK) for regional chemical spray advisories.",
    },
    "Potato___Healthy": {
        "cultural_practices": [
            "Continue regular hill cultivation and balanced nutrient application.",
            "Scout weekly for aphids, blight flecks, and moisture stress.",
        ],
        "sanitation": [
            "Disinfect agricultural tools between field operations.",
        ],
        "prevention": [
            "Maintain uniform soil moisture to avoid tuber cracking or physiological stress.",
        ],
        "disclaimer": "Your potato crop appears healthy with no signs of foliar blight detected.",
    },
    "Potato___Late_Blight": {
        "cultural_practices": [
            "Plant certified disease-free seed potatoes with high field resistance.",
            "Destroy volunteer potato plants and cull piles well before the planting season.",
            "Hill potatoes well to provide at least 4-5 inches of soil cover over developing tubers.",
        ],
        "sanitation": [
            "Remove and destroy heavily blighted plants immediately upon detection in isolated hotspots.",
            "Avoid harvesting during wet weather or when infected foliage remains green.",
        ],
        "prevention": [
            "Schedule irrigation during early morning hours so canopy dries rapidly in sunlight.",
            "Monitor local weather forecasts for sustained cool, humid, overcast conditions favoring Phytophthora.",
        ],
        "disclaimer": "Late Blight spreads rapidly under favorable weather. Consult local KVK or extension officials immediately for official local management advisories.",
    },
    "Rice___Brown_Spot": {
        "cultural_practices": [
            "Apply balanced fertilizers, particularly adequate potassium and silicon, to boost plant resistance.",
            "Correct soil nutrient deficiencies (especially nitrogen and potassium) based on soil test.",
            "Maintain adequate water depth; avoid severe water stress or intermittent drying during tillering.",
        ],
        "sanitation": [
            "Use hot-water treated or certified disease-free seeds.",
            "Remove wild rice grasses and weeds from field bunds.",
        ],
        "prevention": [
            "Incorporate organic matter or green manure to improve soil fertility and microbial diversity.",
            "Soak seeds in clean water and dry thoroughly prior to nursery sowing.",
        ],
        "disclaimer": "This guidance covers agronomic and cultural practices. Consult your local agricultural extension service or Krishi Vigyan Kendra (KVK) for regional chemical spray advisories.",
    },
    "Rice___Healthy": {
        "cultural_practices": [
            "Maintain standard water management according to growth stages (alternate wetting and drying or continuous shallow flooding).",
            "Follow recommended nutrient schedule.",
        ],
        "sanitation": [
            "Keep irrigation channels and bunds free of weed hosts.",
        ],
        "prevention": [
            "Conduct regular periodic field scouting during tillering and panicle initiation.",
        ],
        "disclaimer": "Your rice crop foliage appears healthy with no visible lesion symptoms detected.",
    },
    "Rice___Leaf_Blast": {
        "cultural_practices": [
            "Avoid excessive application of nitrogen fertilizer; split nitrogen into multiple smaller doses.",
            "Plant blast-tolerant or resistant rice cultivars recommended for your agro-climatic zone.",
            "Avoid prolonged drought stress in paddy fields; maintain consistent shallow flooding.",
        ],
        "sanitation": [
            "Burn or compost infected straw and stubble well away from seedbeds.",
            "Clean seed lots to remove light, discolored, or infected grains.",
        ],
        "prevention": [
            "Maintain proper planting density; avoid overly dense seedling transplanting.",
            "Ensure nursery beds are not shaded and receive full sunlight.",
        ],
        "disclaimer": "This guidance covers agronomic and cultural practices. Consult your local agricultural extension service or Krishi Vigyan Kendra (KVK) for regional chemical spray advisories.",
    },
    "Rice___Neck_Blast": {
        "cultural_practices": [
            "Avoid late-season top-dressing with nitrogen fertilizer near panicle emergence.",
            "Maintain consistent water depth during heading and flowering stages to reduce canopy stress.",
            "Use blast-resistant certified cultivars.",
        ],
        "sanitation": [
            "Remove infected panicles and residues after harvest.",
            "Clean and sanitize harvesting and threshing equipment.",
        ],
        "prevention": [
            "Adjust planting time so that flowering does not coincide with rainy, cloudy, high-humidity weeks.",
            "Regularly monitor upper leaves (flag leaves) prior to heading for leaf blast lesions.",
        ],
        "disclaimer": "Neck blast can cause significant yield loss. Consult local Krishi Vigyan Kendra (KVK) immediately for emergency localized crop management.",
    },
    "Sugarcane_Bacterial Blight": {
        "cultural_practices": [
            "Use healthy, certified seed setts sourced from disease-free nurseries.",
            "Practice hot water treatment of seed setts (50°C for 2 hours) or aerated steam treatment where available.",
            "Provide good field drainage to avoid prolonged waterlogging in root zones.",
        ],
        "sanitation": [
            "Sterilize harvesting knives and cutting implements frequently with a disinfectant solution.",
            "Rogue out infected shoots and burn them outside the field.",
        ],
        "prevention": [
            "Avoid ratooning fields that showed severe bacterial blight symptoms.",
            "Plant tolerant varieties recommended by regional sugarcane research stations.",
        ],
        "disclaimer": "This guidance covers agronomic and cultural practices. Consult your local agricultural extension service or Krishi Vigyan Kendra (KVK) for regional chemical spray advisories.",
    },
    "Sugarcane_Healthy": {
        "cultural_practices": [
            "Maintain balanced earthing up and trash mulching for moisture conservation.",
            "Follow prescribed irrigation schedule during formative and grand growth phases.",
        ],
        "sanitation": [
            "Keep inter-row spaces free from weed hosts.",
        ],
        "prevention": [
            "Regularly inspect cane stalks, leaf spindles, and midribs for signs of discoloration.",
        ],
        "disclaimer": "Your sugarcane crop foliage appears healthy with no visible disease symptoms detected.",
    },
    "Sugarcane_Red Rot": {
        "cultural_practices": [
            "Plant certified red rot resistant sugarcane varieties recommended by local research institutes.",
            "Adopt crop rotation with paddy, green manure, or pulses for at least one season.",
            "Select seed setts exclusively from disease-free fields; inspect setts for internal reddening before planting.",
        ],
        "sanitation": [
            "Uproot and burn diseased clumps immediately including root system; do not leave infected stubble.",
            "Avoid taking ratoon crops from infected fields.",
            "Prevent irrigation water from flowing from infected fields to healthy plots.",
        ],
        "prevention": [
            "Avoid deep planting in heavy soils with poor drainage.",
            "Harvest affected crops early to prevent spread to adjacent healthy fields.",
        ],
        "disclaimer": "Red Rot is a serious sugarcane pathogen. Contact your local sugar mill extension officer or Krishi Vigyan Kendra (KVK) immediately for containment protocol.",
    },
    "Wheat___Brown_Rust": {
        "cultural_practices": [
            "Plant rust-resistant wheat varieties adapted to your regional wheat zone.",
            "Avoid early sowing in areas prone to warm, humid early winters.",
            "Ensure balanced application of fertilizers; avoid excessive nitrogen that promotes lush, succulent foliage.",
        ],
        "sanitation": [
            "Eradicate volunteer wheat plants and alternative weed hosts in field borders during off-season.",
        ],
        "prevention": [
            "Scout fields regularly starting from mid-tillering, examining the upper surface of middle and lower leaves.",
            "Ensure adequate plant spacing to allow sun penetration and air movement.",
        ],
        "disclaimer": "This guidance covers agronomic and cultural practices. Consult your local agricultural extension service or Krishi Vigyan Kendra (KVK) for regional chemical spray advisories.",
    },
    "Wheat___Healthy": {
        "cultural_practices": [
            "Maintain recommended irrigation schedule (crown root initiation, tillering, jointing, flowering, milk stage).",
            "Follow balanced N-P-K nutrient application.",
        ],
        "sanitation": [
            "Keep field borders clear of wild grasses.",
        ],
        "prevention": [
            "Continue routine crop scouting throughout reproductive and grain-filling stages.",
        ],
        "disclaimer": "Your wheat crop foliage appears healthy with no visible rust pustules or foliar disease detected.",
    },
    "Wheat___Yellow_Rust": {
        "cultural_practices": [
            "Sow yellow-rust resistant cultivars approved for your zone.",
            "Avoid late sowing; plant at optimal sowing window to build plant resilience before peak rust season.",
            "Monitor fields closely during cool (10-15°C) and humid weather periods.",
        ],
        "sanitation": [
            "Destroy self-sown wheat plants and grass weeds along bunds that act as green bridges.",
        ],
        "prevention": [
            "Maintain balanced fertilization with adequate potassium to strengthen tissue resistance.",
            "Scout leaf surfaces for characteristic yellow-orange pustules arranged in linear stripes.",
        ],
        "disclaimer": "Yellow Rust can spread rapidly under cool, humid conditions. Consult local KVK or extension specialists for immediate localized advisories.",
    },
}


class DiseaseDetectionService:
    """
    Dedicated ML service for FarmSathi Crop Disease Detection.
    Loads and serves the authoritative pre-trained MobileNetV3-Large model
    strictly preserving the 17-class mapping, ImageNet normalization, and eval transforms.
    """

    MODEL_VERSION: str = "farmsathi_disease_mobilenetv3_v1.0"
    ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

    def __init__(self):
        self._model: Optional[nn.Module] = None
        self._classes: Optional[List[str]] = None
        self._metrics: Optional[Dict[str, Any]] = None
        self._model_path_override: Optional[str] = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Deterministic preprocessing pipeline identical to training/evaluation
        self.eval_transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ])

    def set_model_path_override(self, path: Optional[str]) -> None:
        """Allows test suites to point to alternative or missing model paths."""
        self._model_path_override = path
        self._model = None

    def _resolve_path(self, configured_path_str: str) -> Path:
        """Finds artifact paths across root, backend, and relative locations."""
        configured_path = Path(configured_path_str)
        if configured_path.is_absolute() and configured_path.exists():
            return configured_path

        repo_root = Path(__file__).resolve().parents[3]
        backend_root = Path(__file__).resolve().parents[2]

        candidate_paths = [
            Path.cwd() / configured_path,
            repo_root / configured_path,
            backend_root / configured_path,
            repo_root / "ml" / "models" / configured_path.name,
            Path("ml") / "models" / configured_path.name,
            Path("../ml") / "models" / configured_path.name,
            Path("../../ml") / "models" / configured_path.name,
        ]

        for p in candidate_paths:
            if p.exists() and p.is_file():
                return p.resolve()

        return configured_path

    def load_classes(self) -> List[str]:
        """Loads the authoritative 17-class mapping from ml/models/disease_classes.json."""
        if self._classes is not None:
            return self._classes

        classes_path = self._resolve_path(settings.DISEASE_CLASSES_PATH)
        if not classes_path.exists() or not classes_path.is_file():
            logger.error(f"Disease classes file not found at: {classes_path}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "error": "DISEASE_CLASSES_UNAVAILABLE",
                    "message": "Disease classification class mapping is unavailable.",
                    "expected_path": str(classes_path),
                },
            )

        try:
            with open(classes_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._classes = data["classes"]
                return self._classes
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "error": "DISEASE_CLASSES_LOAD_FAILED",
                    "message": f"Failed to load disease classes: {str(exc)}",
                },
            )

    def load_metrics(self) -> Dict[str, Any]:
        """Loads stored evaluation metrics reference from ml/models/disease_eval_metrics.json."""
        if self._metrics is not None:
            return self._metrics

        metrics_path = self._resolve_path(settings.DISEASE_EVAL_METRICS_PATH)
        if not metrics_path.exists() or not metrics_path.is_file():
            logger.warning(f"Disease eval metrics file not found at: {metrics_path}")
            return {}

        try:
            with open(metrics_path, "r", encoding="utf-8") as f:
                self._metrics = json.load(f)
                return self._metrics
        except Exception as exc:
            logger.warning(f"Failed to read disease eval metrics: {str(exc)}")
            return {}

    def load_model(self) -> nn.Module:
        """Loads and verifies the saved MobileNetV3-Large disease model artifact."""
        if self._model is not None:
            return self._model

        classes = self.load_classes()
        num_classes = len(classes)

        model_path = Path(self._model_path_override) if self._model_path_override else self._resolve_path(settings.DISEASE_MODEL_PATH)
        if not model_path.exists() or not model_path.is_file():
            logger.error(f"Disease model weights not found at: {model_path}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "error": "MODEL_UNAVAILABLE",
                    "message": "Disease diagnosis model artifact is unavailable.",
                    "expected_path": str(model_path),
                },
            )

        try:
            # Reconstruct exact trained architecture
            model = models.mobilenet_v3_large(weights=None)
            model.classifier[3] = nn.Sequential(
                nn.Dropout(p=0.3),
                nn.Linear(in_features=1280, out_features=num_classes),
            )

            state_dict = torch.load(model_path, map_location=self.device)
            model.load_state_dict(state_dict)
            model = model.to(self.device)
            model.eval()

            self._model = model
            logger.info(f"Loaded MobileNetV3-Large disease model from {model_path} ({num_classes} classes)")
            return self._model
        except Exception as exc:
            logger.exception("Failed to load disease model weights")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "error": "MODEL_LOAD_FAILED",
                    "message": f"Disease diagnosis model could not be loaded: {str(exc)}",
                    "artifact_path": str(model_path),
                },
            )

    @classmethod
    def format_class_name(cls, raw_class: str) -> Tuple[str, str, str, bool]:
        """
        Parses raw dataset class into farmer-friendly format:
        Returns: (crop, condition, display_name, is_healthy)
        """
        if "___" in raw_class:
            parts = raw_class.split("___", 1)
            crop_raw = parts[0]
            condition_raw = parts[1]
        elif "_" in raw_class:
            parts = raw_class.split("_", 1)
            crop_raw = parts[0]
            condition_raw = parts[1]
        else:
            crop_raw = raw_class
            condition_raw = "Unknown"

        crop = crop_raw.replace("_", " ").strip()
        condition = condition_raw.replace("_", " ").strip()
        is_healthy = "healthy" in condition.lower()

        if is_healthy:
            display_name = f"{crop} - Healthy Plant"
        else:
            display_name = f"{crop} - {condition}"

        return crop, condition, display_name, is_healthy

    def get_management_guidance(self, raw_class: str) -> ManagementGuidance:
        """Retrieves non-chemical agronomic cultural practices and disclaimer for the disease class."""
        info = CULTURAL_MANAGEMENT_KNOWLEDGE.get(
            raw_class,
            {
                "cultural_practices": [
                    "Isolate symptomatic plants to prevent spread.",
                    "Ensure adequate field drainage and proper aeration between crop rows.",
                    "Maintain balanced nutrition based on soil test recommendations.",
                ],
                "sanitation": [
                    "Remove and destroy infected plant debris outside the field.",
                    "Sanitize field tools with bleach or alcohol solution after handling infected plants.",
                ],
                "prevention": [
                    "Plant resistant or tolerant certified cultivars.",
                    "Avoid overhead irrigation during humid weather.",
                ],
                "disclaimer": "This guidance covers agronomic and cultural practices. Consult your local agricultural extension service or Krishi Vigyan Kendra (KVK) for regional chemical spray advisories.",
            },
        )
        return ManagementGuidance(**info)

    def validate_image_file(self, file_bytes: bytes, filename: str, content_type: Optional[str]) -> Image.Image:
        """
        Validates uploaded image file type, size, and integrity.
        Returns opened PIL Image.
        """
        # Validate size
        if len(file_bytes) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty file uploaded. Please upload a valid crop image.",
            )

        if len(file_bytes) > settings.MAX_UPLOAD_SIZE_BYTES:
            max_mb = settings.MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Uploaded file exceeds maximum allowed size of {max_mb} MB.",
            )

        # Validate extension
        ext = Path(filename).suffix.lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file extension '{ext}'. Allowed extensions: {', '.join(sorted(self.ALLOWED_EXTENSIONS))}",
            )

        # Validate MIME type if provided
        if content_type and content_type.lower() not in self.ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type '{content_type}'. Allowed types: JPEG, PNG, WEBP.",
            )

        # Validate image integrity with PIL
        try:
            image = Image.open(io.BytesIO(file_bytes))
            image.verify()  # Verify image integrity
            # Reopen because verify() closes the file
            image = Image.open(io.BytesIO(file_bytes)).convert("RGB")
            return image
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid or corrupted image file: {str(exc)}",
            )

    def assess_image_suitability(
        self,
        image: Image.Image,
        top_confidence: float,
        confidence_margin: float,
    ) -> Tuple[bool, Optional[str]]:
        """
        Evaluates whether the image is suitable for crop disease detection:
        1. Checks botanical foliar presence using HSV hue analysis.
        2. Evaluates confidence against authoritative settings.DISEASE_CONFIDENCE_THRESHOLD
           and margin between top classes.
        """
        try:
            thumb = image.copy()
            thumb.thumbnail((256, 256))
            hsv = thumb.convert("HSV")
            arr = np.array(hsv)
            h, s, v = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]

            # In PIL HSV: H in [25, 110], S >= 25, V >= 25 covers healthy to chlorotic foliage
            foliage_mask = (h >= 25) & (h <= 110) & (s >= 25) & (v >= 25)
            foliage_ratio = float(np.mean(foliage_mask))

            # Broad vegetative hue in [15, 125], S >= 20, V >= 20 covers blight, dry lesions, rusts
            broad_mask = (h >= 15) & (h <= 125) & (s >= 20) & (v >= 20)
            broad_ratio = float(np.mean(broad_mask))

            if foliage_ratio < 0.02:
                return False, "No crop foliage or plant leaf detected in the image."
            if foliage_ratio < 0.15 and broad_ratio < 0.25:
                return False, "Image does not appear to contain crop foliage."
            if (foliage_ratio < 0.25 or confidence_margin < 0.15) and top_confidence < settings.DISEASE_CONFIDENCE_THRESHOLD:
                return False, "Image foliage is indistinct, unclear, or not suitable for crop disease detection."

            return True, None
        except Exception as exc:
            logger.warning(f"Suitability assessment fallback: {exc}")
            return True, None

    def predict(self, image: Image.Image) -> Dict[str, Any]:
        """
        Runs real PyTorch inference on the preprocessed image using MobileNetV3-Large.
        """
        model = self.load_model()
        classes = self.load_classes()

        try:
            tensor = self.eval_transform(image).unsqueeze(0).to(self.device)
            with torch.no_grad():
                outputs = model(tensor)
                probs = torch.softmax(outputs, dim=1)[0]
                top_probs, top_indices = torch.topk(probs, k=min(3, len(classes)))
        except Exception as exc:
            logger.exception("Inference execution failed")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Disease inference execution failed: {str(exc)}",
            )

        top_predictions: List[TopDiseasePrediction] = []
        for prob, idx in zip(top_probs, top_indices):
            raw_c = classes[idx.item()]
            c_crop, c_cond, c_disp, c_healthy = self.format_class_name(raw_c)
            top_predictions.append(
                TopDiseasePrediction(
                    raw_class=raw_c,
                    crop=c_crop,
                    condition=c_cond,
                    display_name=c_disp,
                    is_healthy=c_healthy,
                    probability=round(float(prob.item()), 4),
                )
            )

        best_prediction = top_predictions[0]
        confidence = best_prediction.probability
        is_confident = confidence >= settings.DISEASE_CONFIDENCE_THRESHOLD
        confidence_margin = (
            float(top_probs[0].item() - top_probs[1].item())
            if len(top_probs) > 1
            else float(top_probs[0].item())
        )

        is_suitable, suitability_reason = self.assess_image_suitability(
            image, confidence, confidence_margin
        )

        suitability_message: Optional[str] = None
        if not is_suitable:
            suitability_message = (
                "Please capture or upload a clear close-up photograph of an affected crop leaf."
            )

        uncertainty_notice: Optional[str] = None
        if not is_confident and is_suitable:
            threshold_pct = int(settings.DISEASE_CONFIDENCE_THRESHOLD * 100)
            uncertainty_notice = (
                f"The diagnosis confidence ({int(confidence * 100)}%) is below the {threshold_pct}% threshold. "
                "Foliage symptoms may be in early stages, indistinct, or affected by poor lighting/blur. "
                "For highest accuracy, capture a close-up photo under clear natural light."
            )

        management_guidance = self.get_management_guidance(best_prediction.raw_class)

        return {
            "predicted_condition": best_prediction.raw_class,
            "crop": best_prediction.crop,
            "condition": best_prediction.condition,
            "display_name": best_prediction.display_name,
            "is_healthy": best_prediction.is_healthy,
            "confidence": confidence,
            "is_confident": is_confident,
            "is_suitable": is_suitable,
            "suitability_message": suitability_message,
            "uncertainty_notice": uncertainty_notice,
            "top_predictions": top_predictions,
            "management_guidance": management_guidance,
            "model_version": self.MODEL_VERSION,
        }

    async def diagnose_image(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: Optional[str],
        user: Optional[User],
        session: AsyncSession,
    ) -> DiseaseDiagnosisResponse:
        """
        Full end-to-end diagnosis flow:
        - Validates image file type, size, and integrity
        - Saves image to storage abstraction
        - Performs real MobileNetV3-Large inference
        - For authenticated users, persists to PostgreSQL disease_diagnoses entity
        - For guest users, returns result with id=None, is_saved=False
        """
        # Validate image
        image = self.validate_image_file(file_bytes, filename, content_type)

        # Save to storage abstraction
        stored_path = await storage_service.save_file(
            file_bytes=file_bytes,
            filename=filename,
            content_type=content_type or "image/jpeg",
            subfolder="diseases",
        )

        # Run inference
        result = self.predict(image)
        image_url = f"/uploads/{stored_path}"

        if user is not None:
            # Persist for authenticated user
            record = DiseaseDiagnosis(
                user_id=user.id,
                original_image_path=stored_path,
                predicted_condition=result["predicted_condition"],
                confidence=Decimal(str(round(result["confidence"], 4))),
                model_version=result["model_version"],
                is_confident=result["is_confident"],
                management_guidance=result["management_guidance"].model_dump(),
            )
            session.add(record)
            await session.commit()
            await session.refresh(record)

            return DiseaseDiagnosisResponse(
                id=record.id,
                predicted_condition=record.predicted_condition,
                crop=result["crop"],
                condition=result["condition"],
                display_name=result["display_name"],
                is_healthy=result["is_healthy"],
                confidence=float(record.confidence) if record.confidence is not None else result["confidence"],
                is_confident=record.is_confident,
                is_suitable=result["is_suitable"],
                suitability_message=result["suitability_message"],
                uncertainty_notice=result["uncertainty_notice"],
                top_predictions=result["top_predictions"],
                management_guidance=result["management_guidance"],
                original_image_path=record.original_image_path,
                image_url=image_url,
                model_version=record.model_version,
                is_saved=True,
                created_at=record.created_at,
            )

        # Guest user flow
        return DiseaseDiagnosisResponse(
            id=None,
            predicted_condition=result["predicted_condition"],
            crop=result["crop"],
            condition=result["condition"],
            display_name=result["display_name"],
            is_healthy=result["is_healthy"],
            confidence=result["confidence"],
            is_confident=result["is_confident"],
            is_suitable=result["is_suitable"],
            suitability_message=result["suitability_message"],
            uncertainty_notice=result["uncertainty_notice"],
            top_predictions=result["top_predictions"],
            management_guidance=result["management_guidance"],
            original_image_path=stored_path,
            image_url=image_url,
            model_version=result["model_version"],
            is_saved=False,
            created_at=None,
        )


disease_service = DiseaseDetectionService()
