from testresources import ResourcedTestCase
from testtools import TestCase


class CommandantTestCase(ResourcedTestCase, TestCase):

    def setUp(self):
        TestCase.setUp(self)
        ResourcedTestCase.setUp(self)

    def tearDown(self):
        ResourcedTestCase.tearDown(self)
        TestCase.tearDown(self)
