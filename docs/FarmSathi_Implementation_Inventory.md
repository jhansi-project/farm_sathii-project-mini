# FarmSathi — Implementation Inventory & Quick Reference Matrix

> **Document Type:** Machine- and Team-Friendly Implementation Inventory  
> **Source of Truth:** Authoritative Codebase (`farm_sathii/`)  
> **Audit Status:** Verified against source files, configurations, database models, and test executions  

---

## 1. Project Directory & File Inventory

| Path | Category | Purpose / Description |
| :--- | :--- | :--- |
| `backend/` | Backend Root | Python FastAPI application, database migrations, tests, and dependencies |
| `backend/app/` | Backend Code | Core logic, API routers, database models, repositories, schemas, and services |
| `backend/app/main.py` | ASGI Gateway | FastAPI application entrypoint, CORS configuration, exception handlers, static uploads mount |
| `backend/app/core/config.py` | Configuration | Pydantic `BaseSettings` schema parsing `.env` file |
| `backend/app/core/database.py` | Database Engine | Async SQLAlchemy engine and sessionmaker via `asyncpg` |
| `backend/app/core/security.py` | Security Engine | Argon2 password hashing and JWT encoding/decoding |
| `backend/app/core/languages.py` | Language Registry | Supported language codes, native names, and BCP-47 speech locales |
| `backend/app/api/deps.py` | Security Deps | OAuth2 password bearer schemes, active and optional user resolvers |
| `backend/app/api/v1/router.py` | Router Aggregator | Mounts all 8 endpoint routers into `/api/v1` |
| `backend/app/api/v1/endpoints/` | Controllers | REST route definitions for auth, profile, crops, disease, advisory, weather, history, health |
| `backend/app/models/` | Data Models | SQLAlchemy 2.0 declarative database models (7 tables) |
| `backend/app/repositories/` | Data Access Layer | Database query abstractions isolating SQL operations from business services |
| `backend/app/schemas/` | DTO Contracts | Pydantic v2 validation models for request/response serialization |
| `backend/app/services/` | Business Services | ML inference pipelines, external API adapters, advisory engine |
| `backend/alembic/` | Migrations | Alembic database migration environment and version scripts |
| `backend/alembic/versions/001_initial_schema.py` | Schema Script | DDL migration creating all 7 PostgreSQL tables, indexes, and foreign keys |
| `backend/tests/` | Automated Tests | Pytest suite containing 78 test cases across all domains |
| `backend/requirements.txt` | Dependencies | Python library specifications for web, database, security, and ML |
| `frontend/` | Frontend Root | React 18, TypeScript, and Vite single-page application |
| `frontend/src/app/App.tsx` | Viewport Hub | Tab-based navigation controller, onboarding flow, and global modal mounts |
| `frontend/src/features/` | Feature Views | Production screens: Welcome, Permissions, Dashboard, Crops, Disease, Advisory, History, My Crops |
| `frontend/src/components/layout/` | Layout UI | DashboardLayout, Navbar, BottomNav, LocationModal, PageHeader |
| `frontend/src/components/ui/` | Primitive UI | Button, Card, Input, Modal, Badge, Toast, Spinner, Skeleton, EmptyState |
| `frontend/src/hooks/` | Custom Hooks | `useSpeechRecognition` (Web Speech API) and `usePermissions` |
| `frontend/src/stores/` | State Stores | Zustand stores: `authStore`, `languageStore`, `locationStore` |
| `frontend/src/services/` | API Adapters | Axios REST service clients connecting frontend views to backend endpoints |
| `frontend/src/i18n/` | Localization | `translations.ts` (6 languages) and `useTranslation.ts` hook |
| `frontend/src/styles/` | Design Tokens | `variables.css` (Google Stitch tokens) and `global.css` |
| `frontend/package.json` | Dependencies | NPM specifications for React, Vite, Axios, Zustand, Lucide |
| `ml/` | Machine Learning | Model artifacts, dataset extraction scripts, and training pipelines |
| `ml/models/` | Serialized Models | Production model files (`.pkl`, `.pth`), class maps, and evaluation metrics |
| `ml/datasets/` | Training Datasets | Leaf disease dataset (13,324 images) and stratified split manifest |
| `ml/train_disease_model.py` | Training Pipeline | PyTorch MobileNetV3-Large disease model fine-tuning script |
| `ml/eval_checkpoint.py` | Model Evaluation | Standalone test evaluation script for MobileNetV3 model checkpoint |
| `ml/extract_and_split.py` | Data Preparation | Archive extraction and 70/15/15 stratified dataset partitioner |
| `training/` | Training Notebooks | Crop recommendation training notebook, dataset zip, and duplicate model artifact |
| `training/FarmSathi_Crop_Recommendation_part2 (1).ipynb` | ML Notebook | Complete Exploratory Data Analysis, benchmarking, and training of Random Forest |
| `storage/uploads/` | Media Storage | Filesystem directory for uploaded and diagnosed crop foliage images |
| `.env.example` | Config Template | Environment variable schema and default configuration keys |

---

## 2. Feature Modules Inventory

| Module Code | Module Name | Implementation Layer | Operational Status | Key Highlights |
| :--- | :--- | :--- | :--- | :--- |
| `MOD-AUTH` | Authentication & IAM | Full Stack | **IMPLEMENTED** | Argon2 password hashing, JWT HS256 tokens, profile creation |
| `MOD-PROF` | Farmer Land Profile | Full Stack | **IMPLEMENTED** | Land size, soil type, irrigation source, state, district, village |
| `MOD-CROP` | Crop Recommendation | Full Stack (ML) | **IMPLEMENTED** | 200-tree Random Forest, 7 soil/climate features, 99.55% test accuracy |
| `MOD-DIS` | Plant Disease Diagnosis | Full Stack (DL) | **IMPLEMENTED** | MobileNetV3-Large, 17 classes, 95.92% accuracy, cultural guidance |
| `MOD-ADV` | Natural Language Advisory | Full Stack (NLP) | **IMPLEMENTED** | Native `AgriAdvisoryProvider` expert engine, multi-turn history |
| `MOD-LLM` | Gemini Advisory Provider | Backend Service | **PARTIALLY IMPLEMENTED**| Generative AI via REST; dormant due to unconfigured API key |
| `MOD-WTH` | Agro-Weather & Forecasting | Full Stack | **IMPLEMENTED** | Open-Meteo REST API, 7-day forecast, PostgreSQL cache with 30-min TTL |
| `MOD-GEO` | Location & Geocoding | Full Stack | **IMPLEMENTED** | Open-Meteo search, Nominatim fallback, BigDataCloud reverse geocoding |
| `MOD-HIST` | Unified Activity History | Full Stack | **IMPLEMENTED** | Unified timeline, paginated sub-histories, detail modals |
| `MOD-MYCR` | My Crops Farm Tracker | Frontend View | **IMPLEMENTED** | Browser local storage tracking combined with historical API queries |
| `MOD-VOIC` | Voice Input System | Frontend Hook | **IMPLEMENTED** | Web Speech API across 6 regional Indian BCP-47 speech locales |
| `MOD-CAM` | Hardware Camera Scanner | Frontend View | **IMPLEMENTED** | HTML5 `getUserMedia`, `<canvas>` snapshot, gallery upload fallback |
| `MOD-I18N` | Multilingual Localization | Full Stack | **IMPLEMENTED** | Pure localized dictionaries across English, Telugu, Hindi, Tamil, Kannada, Marathi |
| `MOD-STOR` | File Storage Service | Backend Service | **IMPLEMENTED** | UUID filename generation, directory traversal protection, `/uploads` static mount |
| `MOD-NOTF` | Push Notifications | None | **PLANNED ONLY** | No background push notification service currently implemented |

---

## 3. Complete API Inventory

| Method | Endpoint Route | Request Schema | Response Schema | Auth Required | Controller File |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/` | None | JSON Discovery | No | `backend/app/main.py` |
| `GET` | `/api/v1/health` | None | `StandardResponse[HealthData]` | No | `backend/app/api/v1/endpoints/health.py` |
| `POST` | `/api/v1/auth/register` | `UserRegisterRequest` | `StandardResponse[TokenResponse]` | No | `backend/app/api/v1/endpoints/auth.py` |
| `POST` | `/api/v1/auth/login` | `UserLoginRequest` | `StandardResponse[TokenResponse]` | No | `backend/app/api/v1/endpoints/auth.py` |
| `POST` | `/api/v1/auth/refresh` | `TokenRefreshRequest` | `StandardResponse[AccessTokenResponse]`| No | `backend/app/api/v1/endpoints/auth.py` |
| `GET` | `/api/v1/auth/me` | None | `StandardResponse[UserWithProfileResponse]`| Yes | `backend/app/api/v1/endpoints/auth.py` |
| `GET` | `/api/v1/profile` | None | `StandardResponse[FarmerProfileResponse]`| Yes | `backend/app/api/v1/endpoints/profile.py` |
| `PUT` | `/api/v1/profile` | `FarmerProfileUpdate` | `StandardResponse[FarmerProfileResponse]`| Yes | `backend/app/api/v1/endpoints/profile.py` |
| `POST` | `/api/v1/crops/recommend` | `CropRecommendationRequest` | `StandardResponse[CropRecommendationResponse]`| Optional | `backend/app/api/v1/endpoints/crops.py` |
| `GET` | `/api/v1/crops/history` | Query: `skip`, `limit` | `StandardResponse[List[CropHistoryItem]]` | Yes | `backend/app/api/v1/endpoints/crops.py` |
| `POST` | `/api/v1/diseases/diagnose` | `multipart/form-data` | `StandardResponse[DiseaseDiagnosisResponse]`| Optional | `backend/app/api/v1/endpoints/disease.py` |
| `GET` | `/api/v1/diseases/history` | Query: `skip`, `limit` | `StandardResponse[List[DiseaseHistoryItem]]`| Yes | `backend/app/api/v1/endpoints/disease.py` |
| `GET` | `/api/v1/diseases/model-metrics`| None | `StandardResponse[DiseaseModelMetricsResponse]`| No | `backend/app/api/v1/endpoints/disease.py` |
| `POST` | `/api/v1/advisory/conversations`| `AdvisoryConversationCreate`| `StandardResponse[AdvisoryConversationDetail]`| Yes | `backend/app/api/v1/endpoints/advisory.py` |
| `POST` | `/api/v1/advisory/conversations/{id}/messages`| `AdvisoryMessageCreate`| `StandardResponse[AdvisoryExecutionResponse]`| Yes | `backend/app/api/v1/endpoints/advisory.py` |
| `GET` | `/api/v1/advisory/conversations`| Query: `skip`, `limit` | `StandardResponse[List[ConversationSummary]]`| Yes | `backend/app/api/v1/endpoints/advisory.py` |
| `GET` | `/api/v1/advisory/conversations/{id}`| None | `StandardResponse[AdvisoryConversationDetail]`| Yes | `backend/app/api/v1/endpoints/advisory.py` |
| `DELETE`| `/api/v1/advisory/conversations/{id}`| None | `StandardResponse[bool]` | Yes | `backend/app/api/v1/endpoints/advisory.py` |
| `GET` | `/api/v1/weather/current` | Query: `lat`, `lon`, `name` | `StandardResponse[WeatherResponse]` | No | `backend/app/api/v1/endpoints/weather.py` |
| `GET` | `/api/v1/weather/forecast` | Query: `lat`, `lon`, `days` | `StandardResponse[WeatherResponse]` | No | `backend/app/api/v1/endpoints/weather.py` |
| `GET` | `/api/v1/weather/profile` | None | `StandardResponse[WeatherResponse]` | Yes | `backend/app/api/v1/endpoints/weather.py` |
| `GET` | `/api/v1/weather/search` | Query: `query`, `limit` | `StandardResponse[List[GeocodingResultItem]]`| No | `backend/app/api/v1/endpoints/weather.py` |
| `GET` | `/api/v1/weather/reverse-geocode`| Query: `lat`, `lon` | `StandardResponse[GeocodingResultItem]` | No | `backend/app/api/v1/endpoints/weather.py` |
| `GET` | `/api/v1/history` | Query: `limit` | `StandardResponse[UserHistorySummary]` | Yes | `backend/app/api/v1/endpoints/history.py` |
| `GET` | `/api/v1/history/crop-recommendations`| Query: `skip`, `limit`| `StandardResponse[PaginatedCropHistory]` | Yes | `backend/app/api/v1/endpoints/history.py` |
| `GET` | `/api/v1/history/crop-recommendations/{id}`| None | `StandardResponse[CropHistoryItem]` | Yes | `backend/app/api/v1/endpoints/history.py` |
| `GET` | `/api/v1/history/disease-diagnoses`| Query: `skip`, `limit`| `StandardResponse[PaginatedDiseaseHistory]` | Yes | `backend/app/api/v1/endpoints/history.py` |
| `GET` | `/api/v1/history/disease-diagnoses/{id}`| None | `StandardResponse[DiseaseHistoryItem]` | Yes | `backend/app/api/v1/endpoints/history.py` |
| `GET` | `/api/v1/history/advisory-conversations`| Query: `skip`, `limit`| `StandardResponse[PaginatedAdvisoryHistory]`| Yes | `backend/app/api/v1/endpoints/history.py` |
| `GET` | `/api/v1/history/advisory-conversations/{id}`| None | `StandardResponse[AdvisoryConversationDetail]`| Yes | `backend/app/api/v1/endpoints/history.py` |

---

## 4. Database Models & Schema Table Inventory

| Table Name | Model Class | Primary Key | Foreign Keys & Cascades | Key Columns & Types |
| :--- | :--- | :--- | :--- | :--- |
| `users` | `User` | `id` (UUID) | None | `phone` (VARCHAR, Unique), `email` (VARCHAR, Unique), `password_hash` (VARCHAR), `full_name` (VARCHAR), `is_active` (BOOLEAN) |
| `farmer_profiles` | `FarmerProfile` | `id` (UUID) | `user_id` -> `users.id` (ON DELETE CASCADE) | `preferred_language` (VARCHAR), `land_size_acres` (NUMERIC), `soil_type` (VARCHAR), `irrigation_source` (VARCHAR), `state`, `district`, `village` |
| `crop_recommendations` | `CropRecommendation` | `id` (UUID) | `user_id` -> `users.id` (ON DELETE CASCADE, Nullable)| `nitrogen`, `phosphorus`, `potassium`, `temperature`, `humidity`, `ph`, `rainfall` (NUMERIC), `recommended_crop` (VARCHAR), `top_predictions` (JSON) |
| `disease_diagnoses` | `DiseaseDiagnosis` | `id` (UUID) | `user_id` -> `users.id` (ON DELETE CASCADE, Nullable)| `original_image_path` (VARCHAR), `predicted_condition` (VARCHAR), `confidence` (NUMERIC), `is_confident` (BOOLEAN), `management_guidance` (JSON) |
| `advisory_conversations` | `AdvisoryConversation` | `id` (UUID) | `user_id` -> `users.id` (ON DELETE CASCADE) | `title` (VARCHAR), `language` (VARCHAR), `created_at`, `updated_at` (TIMESTAMPTZ) |
| `advisory_messages` | `AdvisoryMessage` | `id` (UUID) | `conversation_id` -> `advisory_conversations.id` (ON DELETE CASCADE)| `sender_role` (VARCHAR), `message_text` (TEXT), `audio_path` (VARCHAR), `context_used` (JSON) |
| `weather_cache` | `WeatherCache` | `cache_key` (VARCHAR) | None | `latitude`, `longitude` (NUMERIC), `current_conditions` (JSON), `forecast_daily` (JSON), `expires_at` (TIMESTAMPTZ) |

---

## 5. Machine Learning Models & Artifacts Inventory

| Artifact File | Format / Size | Model Architecture | Training Script | Inputs / Output Specs | Measured Accuracy |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `ml/models/farmsathi_crop_recommendation_rf.pkl` | Joblib Pickle<br>7.11 MB (7,281,145 B) | Random Forest<br>(200 Trees, Gini) | `training/FarmSathi_Crop_Recommendation_part2 (1).ipynb` | Input: 7 features (N, P, K, Temp, Humidity, pH, Rain)<br>Output: 22 crop classes | **99.55%** (Test)<br>**99.59%** (5-Fold CV) |
| `ml/models/farmsathi_disease_model.pth` | PyTorch State Dict<br>16.31 MB (17,101,615 B) | MobileNetV3-Large<br>(+ Custom Dropout Head) | `ml/train_disease_model.py` | Input: 224x224 RGB Image<br>Output: 17 pathology classes | **95.92%** (Test)<br>**96.02%** (Macro F1) |
| `ml/models/disease_classes.json` | JSON<br>1,042 Bytes | Class Mapping Metadata | `ml/train_disease_model.py` | 17 class strings & index mapping | N/A |
| `ml/models/disease_eval_metrics.json`| JSON<br>7,017 Bytes | Evaluation Benchmark | `ml/eval_checkpoint.py` | Classification report & 17x17 confusion matrix | N/A |

---

## 6. Datasets & Manifests Inventory

| Dataset Identifier | Location | Total Size / Samples | Target Classes | Train / Val / Test Partition | Source |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Crop Recommendation Dataset** | `training/crop_dataset/Crop_recommendation.csv` | 2,200 rows x 8 columns | 22 agricultural crop classes (100 per class) | 1,760 Train (80%)<br>440 Test (20%) | `training/crop_recommendation_dataset.zip` |
| **Crop Diseases Image Dataset** | `ml/datasets/crop_diseases/Crop Diseases/` | 13,324 leaf images | 17 foliar pathology & healthy classes | 9,322 Train (70%)<br>1,992 Val (15%)<br>2,010 Test (15%) | Extracted via `ml/extract_and_split.py` |
| **Dataset Split Manifest** | `ml/datasets/dataset_split.json` | 2,096,733 Bytes | 17 classes path index | Reproducible split (`seed=42`) | Generated by `extract_and_split.py` |

---

## 7. Training & Evaluation Scripts Inventory

| Script File | Execution Command | Purpose & Description | Output Artifact Generated |
| :--- | :--- | :--- | :--- |
| `training/FarmSathi_Crop_Recommendation_part2 (1).ipynb` | Jupyter Notebook / Google Colab | EDA, multi-model benchmarking (Random Forest vs Gradient Boosting vs XGBoost vs Decision Tree), 5-fold CV, and export | `farmsathi_crop_recommendation_rf.pkl` |
| `ml/extract_and_split.py` | `python ml/extract_and_split.py` | Discovers image classes, validates image files, and creates deterministic 70/15/15 stratified partition | `ml/datasets/dataset_split.json` |
| `ml/train_disease_model.py` | `python ml/train_disease_model.py` | PyTorch training pipeline: class weights, AdamW, Cosine Annealing, early stopping, test evaluation | `ml/models/farmsathi_disease_model.pth`<br>`disease_classes.json`<br>`disease_eval_metrics.json` |
| `ml/eval_checkpoint.py` | `python ml/eval_checkpoint.py` | Standalone validation script running test set inference, measuring latency, and computing confusion matrix | Verified metrics output |

---

## 8. Verification Test Suites Inventory

| Test Module | Total Tests | Execution Status | Core Scenarios Tested |
| :--- | :--- | :--- | :--- |
| `backend/tests/test_health.py` | 1 | **PASSED** | Liveness probe, status healthy, app name, version reporting |
| `backend/tests/test_auth.py` | 6 | **PASSED** | Farmer registration, duplicate phone/email rejection, login, token refresh, `/auth/me` |
| `backend/tests/test_profile.py` | 3 | **PASSED** | Default profile creation, land size/soil update, unauthorized access rejection |
| `backend/tests/test_crops.py` | 6 | **PASSED** | Random Forest inference, top-3 crop probabilities, guest vs authenticated persistence, input validation |
| `backend/tests/test_disease.py` | 8 | **PASSED** | MobileNetV3 inference, image validation, non-foliar image rejection, confidence thresholding, test metrics |
| `backend/tests/test_advisory.py` | 12 | **PASSED** | Conversation creation, message dispatch, safety disclaimers, language propagation |
| `backend/tests/test_advisory_phase9.py` | 8 | **PASSED** | Multimodal image attachment to advisory, capability checks, context assembly validation |
| `backend/tests/test_advisory_scenarios.py`| 10 | **PASSED** | Real farming scenarios: spray before rain, nitrogen deficiency, irrigation timing in regional languages |
| `backend/tests/test_weather.py` | 14 | **PASSED** | Open-Meteo parsing, WMO code mapping, PostgreSQL caching TTL, geocoding fallback, coordinate bounds |
| `backend/tests/test_history_phase10.py` | 6 | **PASSED** | Unified timeline ordering, paginated sub-histories, ownership isolation (cross-user access 404s) |
| `backend/tests/test_models.py` | 3 | **PASSED** | SQLAlchemy table creation, relationship cascading, foreign key constraints |
| `backend/tests/test_postgres_integration.py`| 1 | **PASSED** | Live asynchronous database session creation and query roundtrip |
| **Total Automated Tests** | **78** | **ALL PASSED (0 Failures)** | Full system behavioral verification |

---

## 9. Dependencies Matrix Inventory

### Backend Runtime & ML Dependencies

| Package Name | Installed Version | Category | Primary Role in FarmSathi |
| :--- | :--- | :--- | :--- |
| `fastapi` | 0.141.1 | Web Framework | Core RESTful API routing, dependency injection, and OpenAPI documentation |
| `uvicorn` | 0.53.0 | Web Server | Asynchronous ASGI server running the FastAPI backend |
| `pydantic` | 2.13.5 | Validation | Data modeling, request body parsing, and schema serialization |
| `pydantic-settings` | 2.15.0 | Configuration | Loads typed environment variables from `.env` |
| `sqlalchemy` | 2.0.54 | ORM | Declarative mapping for 7 PostgreSQL database tables |
| `asyncpg` | 0.31.0 | Database Driver | High-speed binary async database connection to PostgreSQL 18 |
| `alembic` | 1.20.0 | Migrations | Automated database schema versioning and execution |
| `passlib` | 1.7.4 | Security | Password hashing orchestration with Argon2 support |
| `argon2-cffi` | 25.1.0 | Security | Cryptographic Argon2 hashing backend |
| `python-jose` | 3.5.0 | Security | JWT token generation, signing, and verification |
| `scikit-learn` | 1.9.1 | Machine Learning | Loads and executes `RandomForestClassifier` for crop recommendation |
| `joblib` | 1.6.0 | Model I/O | Deserializes `farmsathi_crop_recommendation_rf.pkl` |
| `torch` | 2.14.0 | Deep Learning | PyTorch neural network runtime executing MobileNetV3-Large |
| `torchvision` | 0.29.0 | Deep Learning | Image transforms, tensor normalization, and pretrained model architectures |
| `pillow` | 12.3.0 | Image I/O | Decodes, validates, and evaluates leaf foliage image color spaces |
| `pandas` | 3.0.6 | Data Processing | Dataframe construction for crop feature inference inputs |
| `numpy` | 2.5.3 | Numerical Math | Array operations and HSV color mask evaluation |
| `httpx` | 0.28.1 | HTTP Client | Asynchronous client querying Open-Meteo, Nominatim, and BigDataCloud |
| `python-multipart` | 0.0.32 | Web Utilities | Decodes multipart form uploads containing leaf images |
| `pytest` | 9.1.1 | Testing | Automated backend test execution framework |
| `pytest-asyncio` | 1.4.0 | Testing | Asynchronous test loop integration for async database and endpoints |

### Frontend Dependencies

| Package Name | Installed Version | Category | Primary Role in FarmSathi |
| :--- | :--- | :--- | :--- |
| `react` | 18.3.1 | UI Framework | Declarative component tree and virtual DOM reconciliation |
| `react-dom` | 18.3.1 | UI Framework | Browser DOM rendering engine for React |
| `typescript` | 5.4.5 | Language | Static type contracts and interface definition across all frontend code |
| `vite` | 5.2.11 | Build Tooling | Development server with Hot Module Replacement and production Rollup bundler |
| `zustand` | 4.5.2 | State Management | Reactive client stores for authentication, language, and GPS location |
| `axios` | 1.6.8 | HTTP Client | REST client with interceptors for Bearer token injection and refresh |
| `lucide-react` | 0.378.0 | UI Iconography | Icon library providing icons across navigation, weather, and actions |
| `i18next` | 23.11.4 | Localization | Core translation engine underlying the custom `useTranslation` hook |
| `react-i18next` | 14.1.1 | Localization | React bindings for language switching and translations |
| `react-router-dom` | 6.23.0 | Navigation | URL history bindings (complemented by active-tab controller) |

---

## 10. External Integrations & Services Inventory

| Service Provider | API Endpoint Used | Protocol / Format | Authentication | Fallback Behavior |
| :--- | :--- | :--- | :--- | :--- |
| **Open-Meteo Weather** | `https://api.open-meteo.com/v1/forecast` | HTTPS GET / JSON | None (Free open API) | PostgreSQL cached data served if network fails |
| **Open-Meteo Geocoding** | `https://geocoding-api.open-meteo.com/v1/search` | HTTPS GET / JSON | None (Free open API) | Cascades to Nominatim OSM search if empty |
| **OpenStreetMap Nominatim** | `https://nominatim.openstreetmap.org/search`<br>`https://nominatim.openstreetmap.org/reverse`| HTTPS GET / JSON | User-Agent Header | Returns graceful default location ("Current Location", India) |
| **BigDataCloud Client API**| `https://api.bigdatacloud.net/data/reverse-geocode-client` | HTTPS GET / JSON | None (Free client API) | Falls back to Nominatim reverse geocoding |
| **Google Gemini Generative AI**| `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent` | HTTPS POST / JSON | API Key (`GEMINI_API_KEY`) | Seamlessly uses native `AgriAdvisoryProvider` when key is absent |
| **Web Speech API** | Native Browser API (`window.SpeechRecognition`) | W3C Standard | Browser Permission | Instructs farmer to enter text manually if unsupported |
| **HTML5 MediaDevices** | Native Browser API (`navigator.mediaDevices.getUserMedia`) | W3C Standard | Browser Permission | Automatically provides standard file gallery uploader |
