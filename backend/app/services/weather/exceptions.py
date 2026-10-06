class WeatherError(Exception):
    """Base exception for weather service errors."""
    pass


class InvalidCoordinateError(WeatherError):
    """Raised when latitude or longitude are outside valid geographic bounds."""
    pass


class WeatherProviderError(WeatherError):
    """Raised when the weather provider returns an HTTP error or error payload."""
    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.status_code = status_code


class WeatherProviderTimeoutError(WeatherProviderError):
    """Raised when the weather provider request times out."""
    def __init__(self, message: str = "Weather provider request timed out"):
        super().__init__(message, status_code=504)


class WeatherNetworkError(WeatherProviderError):
    """Raised when a network failure occurs contacting the weather provider."""
    def __init__(self, message: str = "Network error connecting to weather provider"):
        super().__init__(message, status_code=502)


class WeatherUnavailableError(WeatherError):
    """Raised when weather data is completely unavailable for a location."""
    pass


class WeatherLocationUnavailableError(WeatherError):
    """Raised when coordinates or location for a farmer profile cannot be resolved."""
    pass

