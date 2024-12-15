from django.test import TestCase
from blog_improved.sgml import (
        ContentModel, 
        ChoiceContentModel,
        ElementDefinition, 
        EntityDefinition,
        LiteralStringValue,
        SequenceContentModel, 
        RepetitionControl,
        OmissionRule,
        SgmlAttribute,
)

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
        attr = SgmlAttribute("id", id_processor, initial_value=None)
        self.assertEqual(attr.name, "id")
