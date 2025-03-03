from enum import Enum
from .file_manager import FileManager

class AssetType(Enum):
    ASSET_MIN = 0
    THEMES = ASSET_MIN
    ASSET_COUNT = 1

class StandardAssets:
    ASSET_TYPE = AssetType
    
    def __init__(self):
        self._asset_dirs = list()
        self.setup_asset_dirs()

    def setup_asset_dirs(self) -> None:
        self._asset_dirs.clear()
        self._asset_dirs.extend([None] * (self.ASSET_TYPE.ASSET_COUNT.value))  # Preallocate list size
        self._asset_dirs[self.ASSET_TYPE.THEMES.value] = "themes"
        assert len(self._asset_dirs) == self.ASSET_TYPE.ASSET_COUNT.value
    
    def get(self) -> list[str]:
        return self._asset_dirs

    def get_asset_dir_name(self, asset) -> str:
        if isinstance(asset, self.ASSET_TYPE):
            return self._asset_dirs[asset.value]
        elif isinstance(asset, str):
            try:
                asset_enum = self.ASSET_TYPE[asset.upper()]
                return self._asset_dirs[asset_enum.value]
            except KeyError:
                raise ValueError(f'The provided asset name "{asset}" is not a matching asset name')
        else:
            return ""

