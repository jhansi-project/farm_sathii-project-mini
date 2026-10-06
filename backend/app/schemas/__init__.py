from app.schemas.common import StandardResponse
from app.schemas.profile import (
    FarmerProfileBase,
    FarmerProfileUpdate,
    FarmerProfileResponse,
)
from app.schemas.user import (
    UserBase,
    UserResponse,
    UserWithProfileResponse,
)
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    TokenRefreshRequest,
    AccessTokenResponse,
)
from app.schemas.crop import (
    CropRecommendationRequest,
    CropRecommendationResponse,
    TopPrediction,
    CropRecommendationHistoryItem,
)
from app.schemas.disease import (
    DiseaseDiagnosisResponse,
    TopDiseasePrediction,
    ManagementGuidance,
    DiseaseHistoryItem,
    DiseaseModelMetricsResponse,
)

from app.schemas.advisory import (
    AdvisoryProviderStatus,
    AdvisoryMessageBase,
    AdvisoryMessageCreate,
    AdvisoryMessageResponse,
    AdvisoryConversationCreate,
    AdvisoryConversationSummary,
    AdvisoryConversationDetail,
    AdvisoryExecutionResponse,
)

from app.schemas.weather import (
    CoordinateQuery,
    CurrentWeatherCondition,
    DailyForecastItem,
    LocationInfo,
    WeatherResponse,
    GeocodingResultItem,
)
from app.schemas.history import (
    HistoryCounts,
    UnifiedHistoryItem,
    UserHistorySummary,
    PaginatedCropHistory,
    PaginatedDiseaseHistory,
    PaginatedAdvisoryHistory,
)

__all__ = [
    "StandardResponse",
    "FarmerProfileBase",
    "FarmerProfileUpdate",
    "FarmerProfileResponse",
    "UserBase",
    "UserResponse",
    "UserWithProfileResponse",
    "UserRegisterRequest",
    "UserLoginRequest",
    "TokenResponse",
    "TokenRefreshRequest",
    "AccessTokenResponse",
    "CropRecommendationRequest",
    "CropRecommendationResponse",
    "TopPrediction",
    "CropRecommendationHistoryItem",
    "DiseaseDiagnosisResponse",
    "TopDiseasePrediction",
    "ManagementGuidance",
    "DiseaseHistoryItem",
    "DiseaseModelMetricsResponse",
    "AdvisoryProviderStatus",
    "AdvisoryMessageBase",
    "AdvisoryMessageCreate",
    "AdvisoryMessageResponse",
    "AdvisoryConversationCreate",
    "AdvisoryConversationSummary",
    "AdvisoryConversationDetail",
    "AdvisoryExecutionResponse",
    "CoordinateQuery",
    "CurrentWeatherCondition",
    "DailyForecastItem",
    "LocationInfo",
    "WeatherResponse",
    "GeocodingResultItem",
    "HistoryCounts",
    "UnifiedHistoryItem",
    "UserHistorySummary",
    "PaginatedCropHistory",
    "PaginatedDiseaseHistory",
    "PaginatedAdvisoryHistory",
]

