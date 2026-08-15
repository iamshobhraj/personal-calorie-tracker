from src.config.settings import Settings, get_settings


def settings_dependency() -> Settings:
    """Provide typed settings to routes that need configuration."""

    return get_settings()
