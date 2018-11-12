import unittest

import youless_python_bridge

class TestYoulessData(unittest.TestCase):

    def test_value(self):
       value = youless_python_bridge.YoulessData(1.232, "w")
       self.assertTrue(value.value() == 1.232)
       se;f.assertTrue(value.unit_of_measurement() == "w")


if __name__ = '__main__':
    unittest.main()
