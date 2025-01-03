from blog_improved.helpers.html_generator import SgmlComponent, make_standard_element
from blog_improved.sgml.sgml_attributes import SgmlAttributeEntry, SgmlAttributes
from blog_improved.themes.settings import get_theme

def make_themed_element(name: str, attrs: dict, attrs_defaults:dict = None, tag_omissions: str = "--") -> SgmlComponent:
    # TODO: return a type of sgmlcomponent suited to themes that change
    theme = get_theme()
    attrs = ThemableSgmlAttributes(attrs, attrs_defaults, theme)
    return SgmlComponent(name, attrs, tag_omissions)

def merge_attributes(sgml_attrs: dict, themed_attrs: dict) -> dict:
    """
    Merges SGML attribute values with themed attribute values.
    The theme attributes take precedence, and for `class`, values are concatenated.

    Args:
        sgml_attrs (dict): A dictionary containing SGML attributes with processors and values
                           (e.g., {"id": {"processor": processor_ref, "value": "my-id"}}).
        themed_attrs (dict): A dictionary containing theme-provided values
                             (e.g., {"class": "linkee"}).

    Returns:
        dict: A dictionary where values from SGML attributes and theme are merged.
              For `class`, values are concatenated; for others, theme takes precedence.
    """
    merged = {}

    for key, attr_data in sgml_attrs.items():
        base_value = attr_data.get('value', '')  # Get the SGML attribute value
        theme_value = themed_attrs.get(key, '')  # Get the theme attribute value

    if key == 'class':
        # Concatenate class values with space separation, ignoring None or empty strings
         merged_value = " ".join(filter(None, [base_value, theme_value])).strip()
    else:
        # Theme value takes precedence; fallback to SGML value if not provided
        merged_value = theme_value or base_value

    merged[key] = merged_value

    # Include additional keys from themed_attrs not in sgml_attrs
    for key, theme_value in themed_attrs.items():
        if key not in merged:
            merged[key] = theme_value

    return merged

def integrate_theme_with_generator(theme, generator):
    """
    Integrates the theme logic with a given generator by updating its components.

    Args:
        theme: An instance of the theme providing attributes for components.
        generator: An instance of a generator that supports registering components.
    """
    # Make a copy of the component keys or items to iterate safely
    registered_components = list(generator.get_registered_components().items())

    for key, component in registered_components:
        # Get the themed attributes for the component
        themed_attrs = theme.get_element_attributes(component.tag)  # Assuming `component.tag` gives the name
        if not themed_attrs:
            continue
        base_attrs = component.attrs.to_dict()  # Convert SgmlAttributes to a dict
        default_attrs = {name: attr["processor"] for name, attr in base_attrs.items()}  # Extract attribute processors
        merged_attrs = merge_attributes(base_attrs, themed_attrs)
        # Create a new themed element
        element = make_themed_element(
            name=component.tag,
            attrs=default_attrs,  # Processors
            attrs_defaults=merged_attrs,  # Initial values
            tag_omissions=component.tag_omissions
        )

        # Remove the existing component
        generator.remove_component(key)

        # Re-register the component with themed attributes
        generator.register_component(key, element)

class ThemableSgmlAttributeEntry(SgmlAttributeEntry):
    """Represents a single SGML attribute with theme integration."""

    def __init__(self, name, processor, theme=None, initial_value=None):
        super().__init__(name, processor, initial_value)
        self.theme = theme  # Store the theme instance

    @SgmlAttributeEntry.value.setter
    def value(self, new_value):
        """
        Sets the value, checking the theme first.
        If the theme has a value for this attribute, merge it with the provided value.
        """
        theme_value = None
        print("checking if theme")
        if self.theme:
            print("checking the new_value")
            print(new_value)
            theme_value = self.theme.get_styles().get(new_value, None)

        # Merge theme value and new value if applicable
        if self.name == "class" and theme_value:
            # Concatenate class attributes with a space
            new_value = f"{theme_value} {new_value}".strip()
        elif theme_value:
            # Use the theme value as a fallback
            new_value = theme_value

        # Set the processed value
        self._value = self.processor(new_value)

class ThemableSgmlAttributes(SgmlAttributes):
    """Holds a collection of themable SGML attributes."""

    def __init__(self, attributes_def=None, initial_values=None, theme=None):
        """
        :param attributes_def: dict of {attribute_name: processor_function}
        :param initial_values: dict of {attribute_name: initial_value}
        :param theme: The theme instance providing attribute defaults.
        """
        self.theme = theme  # Store the theme instance
        super().__init__(attributes_def, initial_values)

    def _create_entry(self, name, processor, initial_value=None):
        """
        Override the entry creation to use ThemableSgmlAttributeEntry.
        """
        return ThemableSgmlAttributeEntry(
            name=name, processor=processor, theme=self.theme, initial_value=initial_value
        )

    def __setitem__(self, key, value):
        """
        Override to apply theme-aware logic when setting an attribute value.
        """
        if key not in self._allowed_keys:
            raise KeyError(f"Cannot add new attribute '{key}' after initialization.")

        # Delegate to the themable entry logic
        self._attributes[key].value = value
