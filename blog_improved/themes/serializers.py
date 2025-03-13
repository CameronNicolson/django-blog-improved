from abc import ABC, abstractmethod
from pathlib import Path
from tomli_w import dumps as toml_dumps
import tomllib

class Serializer(ABC):
    @abstractmethod
    def deserialize():
        pass

    @abstractmethod
    def serialize():
        pass

class TOMLSerializer:

    def deserialize(self, data):
        toml = None
        if not isinstance(data, (Path, str)):
            raise ValueError("TOML deserialize expexts a file path")
        with open(data, "rb") as file: 
            toml = tomllib.load(file)
        return toml

    def serialize(self, data):
        return toml_dumps(data)

