from fastapi import APIRouter
from app.api.v1.endpoints import advisory, auth, crops, disease, health, history, profile, weather

api_v1_router = APIRouter()

# Register endpoint routers
api_v1_router.include_router(health.router)
api_v1_router.include_router(auth.router)
api_v1_router.include_router(profile.router)
api_v1_router.include_router(crops.router)
api_v1_router.include_router(disease.router)
api_v1_router.include_router(advisory.router)
api_v1_router.include_router(weather.router)
api_v1_router.include_router(history.router)



