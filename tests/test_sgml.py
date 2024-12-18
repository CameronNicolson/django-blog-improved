from django.test import TestCase
from datetime import datetime
from blog_improved.utils.strings import (
    to_string_appender,
    normalise_extra_whitespace,
    validate_regex,
    strip_whitespace
)
from blog_improved.sgml import (
    ContentModel, 
    ChoiceContentModel,
    ElementDefinition, 
    EntityDefinition,
    LiteralStringValue,
    SequenceContentModel, 
    RepetitionControl,
    OmissionRule,
    SgmlAttributeEntry,
    SgmlAttributes
)

from blog_improved.helpers.html_generator import id_processor, class_processor

def DATETIME(value):
    # Validate as ISO datetime
    try:
        dt = datetime.fromisoformat(value)
        return dt.isoformat()
    except ValueError:
        raise ValueError("Invalid datetime format.")


class SgmlTestCase(TestCase):
    def test_element_definition(self):
        expected_definition = "<!ELEMENT html - - (head?,body)>"
        element = ElementDefinition(
            name="html",
            content=SequenceContentModel(elements=["head", RepetitionControl(operator="?"), "body"], group_repetition=RepetitionControl(""),
            ),
            tag_omission_rules=OmissionRule("-", "-")
        )

        actual = str(element)
        self.assertEqual(actual, expected_definition)

 
    def test_element_whole_repeat_declaration(self):
        expected_definition = "<!ELEMENT A - - (%inline;)*>"
        element = ElementDefinition(
            name="A",
            content=ContentModel(elements=["%inline;"],
                                 group_repetition=RepetitionControl("*")),
            tag_omission_rules=OmissionRule("-", "-")
        )

        actual = str(element)
        self.assertEqual(actual, expected_definition)

    def test_entity_creation_declaration(self):
        expected_definition = "<!ENTITY % inline \"#PCDATA | %fontstyle; | %phrase; | %special; | %formctrl;\">"
        literal_value = LiteralStringValue(components=[ChoiceContentModel(elements=["#PCDATA", "%fontstyle;", "%phrase;", "%special;", "%formctrl;"], group_repetition=RepetitionControl(""))])
        element = EntityDefinition(
            "inline",
            literal_value,
            parameter=True,
            )
        actual = str(element)
        self.assertEqual(actual, expected_definition)

class SgmlAttributeTestCase(TestCase):
    def test_attribute_creation(self):
        id_processor = lambda value: value 
        attr = SgmlAttributeEntry("id", id_processor, initial_value=None)
        self.assertEqual(attr.name, "id")

class SgmlAttributeEntryTestCase(TestCase):
    def test_attribute_creation(self):
        id_processor = lambda value: value
        attr = SgmlAttributeEntry("id", id_processor, initial_value=None)
        self.assertEqual(attr.name, "id")
        self.assertIsNone(attr.value)

    def test_attribute_with_initial_value(self):
        attr = SgmlAttributeEntry("class", class_processor, initial_value="main-header")
        self.assertEqual(attr.value, "main-header")

    def test_processor_application(self):
        # Processor that uppercases the string
        uppercase_processor = lambda v: v.upper()
        attr = SgmlAttributeEntry("title", uppercase_processor, initial_value="hello")
        self.assertEqual(attr.value, "HELLO")

        attr.value = "world"
        self.assertEqual(attr.value, "WORLD")

    def test_processor_validation(self):
        # ID requires value to start with a letter
        attr = SgmlAttributeEntry("id", id_processor)
        with self.assertRaises(ValueError):
            attr.value = "1invalid"

        # Valid value should not raise
        attr.value = "validId"
        self.assertEqual(attr.value, "validId")

    def test_str_and_repr(self):
        attr = SgmlAttributeEntry("id", id_processor, initial_value="header1")
        self.assertEqual(str(attr), "header1")
        self.assertIn("SgmlAttributeEntry(name='id', value='header1')", repr(attr))


class SgmlAttributesTestCase(TestCase):
    def setUp(self):
        self.attributes_def = {
            "id": id_processor,
            "class": class_processor,
            "datetime": DATETIME
        }

        self.initial_values = {
            "id": "header1",
            "class": "main-header",
            "datetime": "2024-12-13T15:30:00"
        }

    def test_initialization(self):
        attrs = SgmlAttributes(attributes_def=self.attributes_def, initial_values=self.initial_values)
        self.assertIn("id", attrs)
        self.assertIn("class", attrs)
        self.assertIn("datetime", attrs)

        self.assertEqual(attrs["id"], "header1")
        self.assertEqual(attrs["class"], "main-header")
        self.assertEqual(attrs["datetime"], "2024-12-13T15:30:00")

    def test_update_existing_attribute(self):
        attrs = SgmlAttributes(attributes_def=self.attributes_def, initial_values=self.initial_values)
        attrs["id"] = "updatedId"
        self.assertEqual(attrs["id"], "updatedId")

    def test_add_new_attribute_fails(self):
        attrs = SgmlAttributes(attributes_def=self.attributes_def)
        with self.assertRaises(KeyError):
            attrs["new_attr"] = "some value"

    def test_processor_on_update(self):
        attrs = SgmlAttributes(attributes_def=self.attributes_def, initial_values=self.initial_values)
        # Update datetime to another valid ISO datetime
        attrs["datetime"] = "2024-12-14T10:20:30"
        self.assertEqual(attrs["datetime"], "2024-12-14T10:20:30")

        # Invalid datetime should raise ValueError
        with self.assertRaises(ValueError):
            attrs["datetime"] = "invalid-datetime"

    def test_dict_like_methods(self):
        attrs = SgmlAttributes(attributes_def=self.attributes_def, initial_values=self.initial_values)
        keys = set(attrs.keys())
        self.assertEqual(keys, {"id", "class", "datetime"})

        values = list(attrs.values())
        self.assertIn("header1", values)
        self.assertIn("main-header", values)
        self.assertIn("2024-12-13T15:30:00", values)

        items = dict(attrs.items())
        self.assertEqual(items["id"], "header1")
        self.assertEqual(items["class"], "main-header")

    def test_repr(self):
        attrs = SgmlAttributes(attributes_def=self.attributes_def, initial_values=self.initial_values)
        rep = repr(attrs)
        self.assertIn("id='header1'", rep)
        self.assertIn("class='main-header'", rep)

    def test_deletion_not_allowed(self):
        attrs = SgmlAttributes(attributes_def=self.attributes_def, initial_values=self.initial_values)
        with self.assertRaises(TypeError):
            del attrs["id"]

