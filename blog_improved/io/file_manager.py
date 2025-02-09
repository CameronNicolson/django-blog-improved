from enum import Enum
class FileManager:
    theme_dir = "themes"

    class AssetType(Enum): 
        ASSET_LIMIT = 0
        THEME = 1

    def get_theme_dir(self) -> str:
        return theme_dir

    def getAsset(asset_type:AssetType, filename:str) -> str:
        return ""
