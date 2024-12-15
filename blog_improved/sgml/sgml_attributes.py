from blog_improved.utils.strings import StringAppender

def ID(value):
    """ID and NAME tokens must begin with a letter ([A-Za-z]) and may be followed by any number of letters, digits ([0-9]), hyphens ("-"), underscores ("_"), colons (":"), and periods (".")."""
    pass 

# Processor Functions
def ID(value):
    """Ensure value matches SGML ID rules:
    ID and NAME tokens must begin with a letter ([A-Za-z]) and may be followed by
    letters, digits, hyphens, underscores, colons, and periods.
    """
    import re
    pattern = r'^[A-Za-z][A-Za-z0-9\-_:\.]*$'
    if not re.match(pattern, value):
        raise ValueError(f"Invalid ID format for value: {value}")
    return value

def CDATA(value):
    """CDATA could be nearly any string."""
    return value

# Dictionaries of processors
HTML_CORE_ATTRS = {
    "id": ID,          # Ensures correct SGML ID format
    "class": CDATA,    # May hold multiple class tokens
}

ATTRIBUTE_PROCESSORS = {**HTML_CORE_ATTRS}

class SgmlAttributeEntry:
    """Represents a single SGML attribute with a given processor and value."""
    def __init__(self, name, processor, initial_value=None):
        self.name = name
        self.processor = processor
        self._value = None
        if initial_value is not None:
            self.value = initial_value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        # Process and store as StringAppender
        processed = self.processor(new_value)
        if not isinstance(processed, StringAppender):
            processed = StringAppender(processed)
        self._value = processed

    def __str__(self):
        return self.value if self.value is not None else ""

    def __repr__(self):
        return f"SgmlAttributeEntry(name={self.name!r}, value={self.value!r})"


class SgmlAttributes:
    """Holds a collection of SGML attributes defined by name and processor.

    - Attributes must be defined at initialization (name and processor).
    - Values can be assigned later.
    - No new attributes can be added after initialization.
    """

    def __init__(self, attributes_def=None, initial_values=None):
        """
        :param attributes_def: dict of {attribute_name: processor_function}
        :param initial_values: dict of {attribute_name: initial_value}
        """
        if attributes_def is None:
            attributes_def = {}
        if initial_values is None:
            initial_values = {}

        self._attributes = {}
        # Initialize the known attributes
        for name, processor in attributes_def.items():
            initial_value = initial_values.get(name, None)
            attr = SgmlAttributeEntry(name, processor, initial_value=initial_value)
            self._attributes[name] = attr

        # Store allowed keys to prevent adding new ones
        self._allowed_keys = set(self._attributes.keys())

    def __getitem__(self, key):
        if key not in self._attributes:
            raise KeyError(f"{key} not defined.")
        return self._attributes[key].value

    def __setitem__(self, key, value):
        if key not in self._allowed_keys:
            raise KeyError(f"Cannot add new attribute '{key}' after initialization.")
        self._attributes[key].value = value

    def __delitem__(self, key):
        # Decide what to do: either allow deletion or not.
        # If we allow deletion:
        if key not in self._allowed_keys:
            raise KeyError(f"Cannot delete key '{key}' that wasn't initially defined.")
        # This removes the attribute entirely. If you want to forbid deletion, just raise an error.
        raise TypeError(f"Cannot remove attribute '{key}' after its initalisation.")

    def __contains__(self, key):
        return key in self._attributes

    def items(self):
        return ((k, v.value) for k, v in self._attributes.items())

    def keys(self):
        return self._attributes.keys()

    def values(self):
        return (v.value for v in self._attributes.values())

    def __repr__(self):
        cls_name = self.__class__.__name__
        items_repr = ", ".join(f"{k}={v.value!r}" for k, v in self._attributes.items())
        return f"{cls_name}({items_repr})"

