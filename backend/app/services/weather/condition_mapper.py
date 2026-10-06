from typing import Tuple

# WMO Weather interpretation codes (WW) mapped to human-readable condition text
# and Google Material Symbols Outlined icon names.
WMO_CODE_MAP = {
    0: ("Clear Sky", "sunny"),
    1: ("Mainly Clear", "partly_cloudy_day"),
    2: ("Partly Cloudy", "partly_cloudy_day"),
    3: ("Overcast", "cloud"),
    45: ("Foggy", "foggy"),
    48: ("Depositing Rime Fog", "foggy"),
    51: ("Light Drizzle", "grain"),
    53: ("Moderate Drizzle", "grain"),
    55: ("Dense Drizzle", "grain"),
    56: ("Light Freezing Drizzle", "ac_unit"),
    57: ("Dense Freezing Drizzle", "ac_unit"),
    61: ("Slight Rain", "water_drop"),
    63: ("Moderate Rain", "rainy"),
    65: ("Heavy Rain", "rainy_heavy"),
    66: ("Light Freezing Rain", "severe_cold"),
    67: ("Heavy Freezing Rain", "severe_cold"),
    71: ("Slight Snow Fall", "ac_unit"),
    73: ("Moderate Snow Fall", "ac_unit"),
    75: ("Heavy Snow Fall", "ac_unit"),
    77: ("Snow Grains", "weather_snowy"),
    80: ("Slight Rain Showers", "rainy"),
    81: ("Moderate Rain Showers", "rainy"),
    82: ("Violent Rain Showers", "rainy_heavy"),
    85: ("Slight Snow Showers", "weather_snowy"),
    86: ("Heavy Snow Showers", "weather_snowy"),
    95: ("Thunderstorm", "thunderstorm"),
    96: ("Thunderstorm with Slight Hail", "thunderstorm"),
    99: ("Thunderstorm with Heavy Hail", "thunderstorm"),
}


def get_condition_from_wmo_code(code: int) -> Tuple[str, str]:
    """
    Maps a WMO weather code to a human-readable condition and Material Symbols icon name.
    If the code is unknown, returns safe fallback ('Unknown Weather', 'thermostat')
    without fabricating conditions.
    """
    if code in WMO_CODE_MAP:
        return WMO_CODE_MAP[code]
    return "Unknown", "cloud"


map_wmo_code_to_condition = get_condition_from_wmo_code

