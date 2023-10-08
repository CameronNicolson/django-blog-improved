from django.test import TestCase
from blog_improved.models import Status

class StatusTestCase(TestCase): 

    def test_name_to_id_publish(self):
        public_post_id_actual = Status.name_to_id("publish")
        public_post_id_expected = 1
        self.assertEquals(public_post_id_actual, public_post_id_expected)


    def test_name_to_id_private(self):
        private_post_id_actual = Status.name_to_id("private")
        private_post_id_expected = 2
        self.assertEquals(private_post_id_actual, private_post_id_expected)


    def test_name_to_id_unlisted(self):
        unlisted_post_id_actual = Status.name_to_id("unlisted")
        unlisted_post_id_expected = 3
        self.assertEquals(unlisted_post_id_actual, unlisted_post_id_expected)


    def test_name_to_id_draft(self):
        draft_post_id_actual = Status.name_to_id("draft")
        draft_post_id_expected = 0
        self.assertEquals(draft_post_id_actual, draft_post_id_expected)

    def test_name_to_id_mixed_casing(self):
        public_post_id_actual = Status.name_to_id("pUBliSh")
        public_post_id_expected = 1
        self.assertEquals(public_post_id_actual, public_post_id_expected)


    def test_name_to_id_upper_casing(self):
        public_post_id_actual = Status.name_to_id("PUBLISH")
        public_post_id_expected = 1
        self.assertEquals(public_post_id_actual, public_post_id_expected)

    def test_name_to_id_unknown_value_error(self):
        try:
            deleted_post_id = Status.name_to_id("deleted")
        except ValueError as e:
            self.assertEqual(str(e), "Unknown status with name 'deleted'")
        else:
            self.fail("ValueError was not raised")

    def test_name_to_id_type_error(self):
        try:
            deleted_post_id = Status.name_to_id(333)
        except TypeError as e:
            self.assertEqual(str(e), "Argument 'name' must be a string")
        else:
            self.fail("TypeError was not raised")

    def test_name_to_id_empty_string_error(self):
        try:
            deleted_post_id = Status.name_to_id("")
        except ValueError as e:
            self.assertEqual(str(e), "Argument 'name' cannot be an empty string")
        else:
            self.fail("ValueError was not raised")

