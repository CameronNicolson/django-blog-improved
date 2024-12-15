import sys
import unittest
from tests.test_sgml import SgmlTestCase, SgmlAttributeTestCase

def suite(key):
    if key == "html":
        return unittest.makeSuite(SgmlTestCase)
    else:
        print(f"Test suite '{key}' is not a recognised test.")
        return sys.exit(1)
