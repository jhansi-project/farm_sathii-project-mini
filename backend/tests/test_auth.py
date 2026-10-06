import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_with_phone_success(async_client: AsyncClient):
    unique_phone = f"+9198{uuid.uuid4().hex[:8]}"
    payload = {
        "full_name": "Balwinder Singh",
        "phone": unique_phone,
        "password": "SecurePassword123!",
        "preferred_language": "pa",
    }
    response = await async_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert "refresh_token" in data["data"]
    assert data["data"]["user"]["phone"] == unique_phone
    assert data["data"]["user"]["full_name"] == "Balwinder Singh"
    assert data["data"]["user"]["profile"]["preferred_language"] == "pa"


@pytest.mark.asyncio
async def test_register_duplicate_phone_fails(async_client: AsyncClient):
    unique_phone = f"+9197{uuid.uuid4().hex[:8]}"
    payload = {
        "full_name": "Farmer Duplicate",
        "phone": unique_phone,
        "password": "Password123!",
    }
    # First registration
    res1 = await async_client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == 201

    # Duplicate registration
    res2 = await async_client.post("/api/v1/auth/register", json=payload)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"]


@pytest.mark.asyncio
async def test_register_with_email_success(async_client: AsyncClient):
    unique_email = f"farmer_{uuid.uuid4().hex[:8]}@example.com"
    payload = {
        "full_name": "Suresh Patel",
        "email": unique_email,
        "password": "PatelPassword123!",
        "preferred_language": "gu",
    }
    response = await async_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["user"]["email"] == unique_email


@pytest.mark.asyncio
async def test_register_no_identifier_fails(async_client: AsyncClient):
    payload = {
        "full_name": "No Identifier",
        "password": "Password123!",
    }
    response = await async_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success_and_lifecycle(async_client: AsyncClient):
    unique_phone = f"+9196{uuid.uuid4().hex[:8]}"
    pwd = "FarmerSecret@456"

    # Register
    reg_res = await async_client.post(
        "/api/v1/auth/register",
        json={"full_name": "Anil Deshmukh", "phone": unique_phone, "password": pwd},
    )
    assert reg_res.status_code == 201

    # Login
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"identifier": unique_phone, "password": pwd},
    )
    assert login_res.status_code == 200
    login_data = login_res.json()["data"]
    access_token = login_data["access_token"]
    refresh_token = login_data["refresh_token"]

    # Access protected /me
    me_res = await async_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert me_res.status_code == 200
    assert me_res.json()["data"]["full_name"] == "Anil Deshmukh"

    # Refresh token
    refresh_res = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_res.status_code == 200
    new_access_token = refresh_res.json()["data"]["access_token"]
    assert new_access_token != ""


@pytest.mark.asyncio
async def test_login_invalid_password_fails(async_client: AsyncClient):
    unique_phone = f"+9195{uuid.uuid4().hex[:8]}"
    await async_client.post(
        "/api/v1/auth/register",
        json={"full_name": "Test User", "phone": unique_phone, "password": "CorrectPassword"},
    )
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"identifier": unique_phone, "password": "WrongPassword"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_without_token(async_client: AsyncClient):
    response = await async_client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "invalid_name",
    ["", "   ", "12345", "Jhansi123", "@@@", "123@@", "nsdkjf123", "..", "A"],
)
async def test_register_invalid_full_name_fails(async_client: AsyncClient, invalid_name: str):
    unique_phone = f"+9198{uuid.uuid4().hex[:8]}"
    payload = {
        "full_name": invalid_name,
        "phone": unique_phone,
        "password": "SecurePassword123!",
    }
    response = await async_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "valid_name",
    ["Jhansi", "Jhansi Reddy", "A. Kumar", "Mary-Jane", "O'Connor", "K. V. Raman"],
)
async def test_register_valid_full_name_succeeds(async_client: AsyncClient, valid_name: str):
    unique_phone = f"+9198{uuid.uuid4().hex[:8]}"
    payload = {
        "full_name": valid_name,
        "phone": unique_phone,
        "password": "SecurePassword123!",
    }
    response = await async_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    assert response.json()["data"]["user"]["full_name"] == valid_name.strip()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "invalid_email",
    ["26323", "abc", "abc@", "@gmail.com", "abc@gmail"],
)
async def test_register_invalid_email_fails(async_client: AsyncClient, invalid_email: str):
    payload = {
        "full_name": "Ramesh Kumar",
        "email": invalid_email,
        "password": "SecurePassword123!",
    }
    response = await async_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "invalid_phone",
    ["26323", "123", "abcdef", "@@@"],
)
async def test_register_invalid_phone_fails(async_client: AsyncClient, invalid_phone: str):
    payload = {
        "full_name": "Ramesh Kumar",
        "phone": invalid_phone,
        "password": "SecurePassword123!",
    }
    response = await async_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "invalid_password",
    ["", "   ", "12345", "abc", "21332133"],
)
async def test_register_invalid_password_fails(async_client: AsyncClient, invalid_password: str):
    unique_phone = f"+9198{uuid.uuid4().hex[:8]}"
    payload = {
        "full_name": "Ramesh Kumar",
        "phone": unique_phone,
        "password": invalid_password,
    }
    response = await async_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422

