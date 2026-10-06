from app.repositories.base import BaseRepository
from app.repositories.user_repo import UserRepository
from app.repositories.profile_repo import FarmerProfileRepository
from app.repositories.crop_repo import CropRecommendationRepository
from app.repositories.disease_repo import DiseaseDiagnosisRepository
from app.repositories.advisory_repo import AdvisoryRepository
from app.repositories.weather_repo import WeatherCacheRepository

__all__ = [
    "BaseRepository",
    "UserRepository",
    "FarmerProfileRepository",
    "CropRecommendationRepository",
    "DiseaseDiagnosisRepository",
    "AdvisoryRepository",
    "WeatherCacheRepository",
]
