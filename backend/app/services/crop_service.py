import os
import uuid
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib
import pandas as pd
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.crop_recommendation import CropRecommendation
from app.models.user import User
from app.schemas.crop import (
    CropRecommendationRequest,
    CropRecommendationResponse,
    TopPrediction,
)


class CropRecommendationService:
    """
    Dedicated ML service for FarmSathi Crop Recommendation.
    Loads and serves the authoritative pre-trained Random Forest model
    strictly preserving the 7-feature contract without preprocessing/scaling.
    """

    FEATURE_ORDER: List[str] = [
        "N",
        "P",
        "K",
        "temperature",
        "humidity",
        "ph",
        "rainfall",
    ]
    MODEL_VERSION: str = "farmsathi_crop_rf_v1.0"

    def __init__(self):
        self._model = None
        self._model_path_override: Optional[str] = None

    def set_model_path_override(self, path: Optional[str]) -> None:
        """Allows test suites to point to alternative or missing paths."""
        self._model_path_override = path
        self._model = None

    def _resolve_model_path(self) -> Path:
        """Finds the model artifact across valid workspace and backend locations."""
        if self._model_path_override:
            return Path(self._model_path_override)

        configured_path = Path(settings.CROP_MODEL_PATH)
        if configured_path.is_absolute() and configured_path.exists():
            return configured_path

        # Candidate locations relative to current working directory and module path
        repo_root = Path(__file__).resolve().parents[3]
        backend_root = Path(__file__).resolve().parents[2]

        candidate_paths = [
            Path.cwd() / configured_path,
            repo_root / configured_path,
            backend_root / configured_path,
            repo_root / "ml" / "models" / "farmsathi_crop_recommendation_rf.pkl",
            repo_root / "training" / "farmsathi_crop_recommendation_rf.pkl",
            Path("ml/models/farmsathi_crop_recommendation_rf.pkl"),
            Path("training/farmsathi_crop_recommendation_rf.pkl"),
            Path("../ml/models/farmsathi_crop_recommendation_rf.pkl"),
            Path("../training/farmsathi_crop_recommendation_rf.pkl"),
        ]

        for p in candidate_paths:
            if p.exists() and p.is_file():
                return p.resolve()

        # If not found, return the configured path for reporting
        return configured_path

    def load_model(self):
        """Loads and verifies the serialized Random Forest model artifact."""
        if self._model is not None:
            return self._model

        model_path = self._resolve_model_path()
        if not model_path.exists() or not model_path.is_file():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "error": "MODEL_UNAVAILABLE",
                    "message": "Crop recommendation model artifact is unavailable.",
                    "expected_path": str(model_path),
                },
            )

        try:
            loaded_artifact = joblib.load(model_path)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "error": "MODEL_LOAD_FAILED",
                    "message": f"Crop recommendation model could not be loaded: {str(exc)}",
                    "artifact_path": str(model_path),
                },
            )

        # Integrity checks
        if not hasattr(loaded_artifact, "predict") or not hasattr(
            loaded_artifact, "predict_proba"
        ):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "error": "INVALID_MODEL_INTERFACE",
                    "message": "Loaded model artifact lacks required predict or predict_proba methods.",
                },
            )

        n_features = getattr(loaded_artifact, "n_features_in_", None)
        if n_features is not None and n_features != len(self.FEATURE_ORDER):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "error": "FEATURE_MISMATCH",
                    "message": f"Model expects {n_features} features, but contract requires {len(self.FEATURE_ORDER)}.",
                },
            )

        self._model = loaded_artifact
        return self._model

    def predict(self, req: CropRecommendationRequest) -> Dict[str, Any]:
        """
        Executes real inference on the input request.
        Preserves exact feature order [N, P, K, temperature, humidity, ph, rainfall].
        No scaling or preprocessing applied.
        """
        model = self.load_model()

        inputs_dict: Dict[str, float] = {
            "N": float(req.nitrogen),
            "P": float(req.phosphorus),
            "K": float(req.potassium),
            "temperature": float(req.temperature),
            "humidity": float(req.humidity),
            "ph": float(req.ph),
            "rainfall": float(req.rainfall),
        }

        # Build DataFrame with exact feature order
        input_df = pd.DataFrame([inputs_dict])[self.FEATURE_ORDER]

        try:
            pred_crop = model.predict(input_df)[0]
            probs = model.predict_proba(input_df)[0]
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Inference execution failed: {str(exc)}",
            )

        classes = model.classes_
        top_indices = probs.argsort()[::-1][:3]
        top_predictions = [
            {
                "crop": str(classes[idx]),
                "probability": round(float(probs[idx]), 4),
            }
            for idx in top_indices
        ]

        return {
            "recommended_crop": str(pred_crop),
            "top_predictions": top_predictions,
            "inputs": inputs_dict,
            "model_version": self.MODEL_VERSION,
        }

    async def recommend_crop(
        self,
        req: CropRecommendationRequest,
        user: Optional[User],
        session: AsyncSession,
    ) -> CropRecommendationResponse:
        """
        Handles end-to-end recommendation flow:
        - Evaluates prediction using verified Random Forest artifact
        - If authenticated, saves recommendation history to PostgreSQL
        - If guest, returns prediction without persistence
        """
        result = self.predict(req)

        if user is not None:
            # Persist to database for authenticated user
            record = CropRecommendation(
                user_id=user.id,
                nitrogen=Decimal(str(req.nitrogen)),
                phosphorus=Decimal(str(req.phosphorus)),
                potassium=Decimal(str(req.potassium)),
                temperature=Decimal(str(req.temperature)),
                humidity=Decimal(str(req.humidity)),
                ph=Decimal(str(req.ph)),
                rainfall=Decimal(str(req.rainfall)),
                recommended_crop=result["recommended_crop"],
                top_predictions=result["top_predictions"],
                model_version=result["model_version"],
            )
            session.add(record)
            await session.commit()
            await session.refresh(record)

            return CropRecommendationResponse(
                id=record.id,
                recommended_crop=record.recommended_crop,
                top_predictions=[
                    TopPrediction(**p) for p in record.top_predictions
                ],
                inputs=result["inputs"],
                model_version=record.model_version,
                is_saved=True,
                created_at=record.created_at,
            )

        # Guest user flow
        return CropRecommendationResponse(
            id=None,
            recommended_crop=result["recommended_crop"],
            top_predictions=[
                TopPrediction(**p) for p in result["top_predictions"]
            ],
            inputs=result["inputs"],
            model_version=result["model_version"],
            is_saved=False,
            created_at=None,
        )


crop_service = CropRecommendationService()
