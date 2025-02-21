from typing import Callable, Optional
from blog_improved.formatters.html.html_generator import SgmlComponent, make_standard_element
from blog_improved.sgml import ElementDefinition 
from blog_improved.sgml.sgml_attributes import SgmlAttributeEntry, SgmlAttributes
from blog_improved.themes.settings import get_theme

def make_themed_element(
    element_factory: SgmlComponent,
    theme: Optional[dict] = None
    ) -> SgmlComponent:
    """
    Create a themed SGML element, preserving the behavior of the old element factory.

    Args:
        element_factory: The original factory function for creating the element (e.g., make_hierarchical_element).
        theme: An optional theme dictionary for applying themed attributes.
        *args: Positional arguments to pass to the original factory function.
        **kwargs: Keyword arguments to pass to the original factory function.

    Returns:
        SgmlComponent: The newly created SGML component with themed attributes applied.
    """
    # Step 1: Create the element using the original factory
    original_element = element_factory

    # Step 2: Apply the theme
    if theme is None:
        theme = get_theme()  # Use the global theme if none is provided

    # Merge attributes for the component
    merged_attrs, default_attrs = get_merged_attributes(theme, original_element)

    # Step 3: Create a new SgmlComponent with updated attributes
    updated_attrs = ThemableSgmlAttributes(default_attrs, merged_attrs, theme)
    return SgmlComponent(
        tag=original_element.tag,
        attrs=updated_attrs,
        tag_omissions=original_element.tag_omissions,
        level_range=getattr(original_element, "level_range", None)
    )

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
        base_value = attr_data.get("value", "")  # Get the SGML attribute value
        theme_value = themed_attrs.get(key, "")  # Get the theme attribute value

    if key == "class":
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
        # Merge attributes for the component
        merged_attrs, default_attrs = get_merged_attributes(theme, component)
        if not merged_attrs:
            continue

        # Create a new themed element
        element = make_themed_element(
            element_factory=component,
        )
        # Remove the existing component
        generator.remove_component(key)

        # Re-register the component with themed attributes
        generator.register_component(key, element)



def get_merged_attributes(theme, component):
    """
    Retrieve and merge themed attributes with the base attributes for a component.

    Args:
        theme: The theme providing attributes for components.
        component: The component whose attributes need to be merged.

    Returns:
        A tuple containing:
        - merged_attrs: The merged attributes (theme + base).
        - default_attrs: The default attributes with their processors.
    """
    # Determine themed attributes for the component
    themed_attrs = None
    if hasattr(component.tag, "__iter__") and not isinstance(component.tag, str):
        # Iterate over tags in the iterable and merge themed attributes
        themed_attrs = {}
        for tag in component.tag:
            tag_attrs = theme.get_element_attributes(tag.lower())
            if tag_attrs:
                themed_attrs.update(tag_attrs)
    else:
        # Handle single string tags
        themed_attrs = theme.get_element_attributes(str(component.tag).lower())

    if not themed_attrs:
        return (None, None,)

    # Base attributes from the component
    base_attrs = component.attrs.to_dict()  # Convert SgmlAttributes to a dict
    default_attrs = {name: attr["processor"] for name, attr in base_attrs.items()}  # Extract attribute processors
    merged_attrs = merge_attributes(base_attrs, themed_attrs)

    return merged_attrs, default_attrs

class ThemableSgmlAttributeEntry(SgmlAttributeEntry):
    """Represents a single SGML attribute with theme integration."""

    def __init__(self, name, processor, theme=None, initial_value=None):
        super().__init__(name, processor, initial_value)
        self.theme = theme  # Store the theme instance

    @property
    def value(self):
        """Retrieve the value, applying theming if applicable."""
        if self.theme:
            # Check if the value needs to be resolved through the theme
            themed_value = self.theme.get_styles().get(self._value)
            if themed_value:
                return self.processor(f"{self._value} {themed_value}")
        return super().value

    @value.setter
    def value(self, new_value):
        """Set the value."""
        super(ThemableSgmlAttributeEntry, self.__class__).value.fset(self, new_value)

class ThemableSgmlAttributes(SgmlAttributes):
    """Holds a collection of themable SGML attributes."""

    def __init__(self, attributes_def=None, initial_values=None, theme=None):
        """
        :param attributes_def: dict of {attribute_name: processor_function}
        :param initial_values: dict of {attribute_name: initial_value}
        :param theme: The theme instance providing attribute defaults.
        """
        super().__init__(attributes_def, initial_values)

        self.theme = theme
        self.lookup_styles = self.theme.get_styles() or {}
        # Initialize the known attributes
        for name, processor in attributes_def.items():
            initial_value = initial_values.get(name, None)
            lookup_style = self.lookup_styles.get(name, False)
            if lookup_style:
                attr = ThemableSgmlAttributeEntry(
                    name=name, processor=processor, theme=theme, initial_value=initial_value
                )
            else:
                attr = SgmlAttributeEntry(name=name, processor=processor, initial_value=initial_value)
            self._attributes[name] = attr

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

    def update(self, values):
        """
        Update existing attributes with new values, creating themable or regular entries as needed.
        """
        for key, value in values.items():
            if key not in self._allowed_keys:
                raise KeyError(f"Cannot add new attribute '{key}' after initialization.")
            processor = self._attributes[key].processor  # Use the existing processor
            if key == "class":
                if isinstance(value, str):
                    lookup_style = value.strip().split(" ")
                else:
                    lookup_style = value

                for name in lookup_style:
                    theme_style = self.lookup_styles.get(name, False)
                    base_value = name
                    if theme_style:
                        self._attributes[key] = ThemableSgmlAttributeEntry(
                        name=key, processor=processor, theme=self.theme, initial_value=name
                        )
            else:
                # Replace with a regular SgmlAttributeEntry
                self._attributes[key] = SgmlAttributeEntry(
                        name=key, processor=processor, initial_value=value
                        )

def get_theme_width_map():
    theme = get_theme()
    return theme.width_scale

def get_theme_grid():
    theme = get_theme()
    return theme.grid_properties

