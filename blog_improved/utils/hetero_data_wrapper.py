class HeteroDataWrapper:
    def __init__(self, data, start=0):
        if not isinstance(data, (tuple, dict)):
            raise TypeError("Data must be a tuple or dictionary")
        self._data = data
        self._saved_access = [None for _ in range(start)]
        self._index = start

    def __getitem__(self, key):
        if isinstance(self._data, dict):
            return self._data[key]
        elif isinstance(self._data, tuple):
            matched = next((i for i, val in enumerate(self._saved_access) if key == val), None)
            if matched:
                return self._data[matched]
            if self._index >= len(self._data):
                raise IndexError("Tuple index out of range")
            value = self._data[self._index]
            self._saved_access.append(key)
            self._index += 1
            return value

    def reset(self):
        """Resets the tuple index to 0."""
        if isinstance(self._data, tuple):
            self._index = 0
