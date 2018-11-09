from unittest import TestCase

import youless_python_bridge

class TestYoulessData(TestCase):
    def test_value(self):
       value = youless_python_bridge.YoulessData(1.232, "w")
       self.assertTrue(value.value() == 1.232)
       se;f.assertTrue(value.unit_of_measurement() == "w")
