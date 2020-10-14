import unittest
from youless_api.youless_api import YoulessAPI


class MyTestCase(unittest.TestCase):
    def test_something(self):
        api = YoulessAPI("192.168.1.104")
        api.update()
        gas = api.gas_meter

        self.assertTrue(gas.unit_of_measurement == 'm3')
        self.assertLess(gas.value, 2)


if __name__ == '__main__':
    unittest.main()
