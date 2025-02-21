import sys
from unittest import makeSuite, TestSuite
from tests.test_sgml import SgmlTestCase, SgmlAttributeEntryTestCase, SgmlAttributesTestCase

def suite(key):
    if key == "html":
        return TestSuite([
                    makeSuite(SgmlTestCase),
                    makeSuite(SgmlAttributeEntryTestCase),
                    makeSuite(SgmlAttributesTestCase)
                ])
    else:
        print(f"Test suite '{key}' is not a recognised test.")
        return sys.exit(1)
