from django.test import TestCase

class BasicTest(TestCase):

    def test_basic_math(self):
        self.assertEqual(2 + 2, 24)