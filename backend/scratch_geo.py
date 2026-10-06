import httpx
import asyncio

async def test():
    queries = [
        "miyapur,telangana",
        "Miyapur, Telangana",
        "miyapur",
        "Miyapur",
        "Miyapur, Hyderabad",
        "Miyapur, Hyderabad, Telangana",
        "Hyderabad",
        "Tirupati",
        "Bowrampet",
        "Bowrampet, Dundigal",
        "Dundigal",
    ]
    headers = {"User-Agent": "FarmSathi-DigitalAgriculture/1.0"}
    async with httpx.AsyncClient(headers=headers, timeout=10.0) as client:
        print("=== OPEN-METEO GEOCODING ===")
        for q in queries:
            try:
                r = await client.get("https://geocoding-api.open-meteo.com/v1/search", params={"name": q, "count": 5, "format": "json"})
                results = r.json().get("results") or []
                print(f"Open-Meteo [{q}]: {len(results)} results")
                for res in results[:2]:
                    print(f"   -> {res.get('name')}, {res.get('admin1')}, {res.get('country')}")
            except Exception as e:
                print(f"Open-Meteo [{q}] Error: {e}")

        print("\n=== NOMINATIM OPENSTREETMAP ===")
        for q in queries:
            try:
                r = await client.get("https://nominatim.openstreetmap.org/search", params={"q": q, "format": "json", "countrycodes": "in", "limit": 5})
                results = r.json() if isinstance(r.json(), list) else []
                print(f"Nominatim [{q}]: {len(results)} results")
                for res in results[:2]:
                    print(f"   -> {res.get('display_name')[:60]} ({res.get('lat')}, {res.get('lon')})")
            except Exception as e:
                print(f"Nominatim [{q}] Error: {e}")

if __name__ == "__main__":
    asyncio.run(test())
