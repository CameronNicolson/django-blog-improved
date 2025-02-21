_formatter_env_settings: dict = {}

def set_env_settings(settings: dict):  # Function to populate settings
    global _formatter_env_settings
    _formatter_env_settings.update(settings)  # Merge with existing settings

def get_env_setting(setting_name: str):
    return _formatter_env_settings.get(setting_name)
