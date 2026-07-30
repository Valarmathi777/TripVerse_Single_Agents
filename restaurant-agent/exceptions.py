class RestaurantAgentException(Exception):
    """Base exception for all RestaurantAgent errors."""
    pass

class PreferenceParsingError(RestaurantAgentException):
    """Raised when user preference parsing fails."""
    pass

class ProviderAPIError(RestaurantAgentException):
    """Raised when external API provider (Gemini or Places) fails."""
    pass

class DataNotFoundException(RestaurantAgentException):
    """Raised when no matching restaurant candidates could be found."""
    pass
