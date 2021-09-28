import unittest
import datetime

from unittest.mock import patch, Mock
from youless_api.devices import LS120, LS110, LS120PVOutput
from youless_api.const import STATE_OK, STATE_FAILED


class MockResponse:

    def __init__(self):
        self._ok = False
        self._json = lambda: 0
        self._headers = {}
        self._text = ''

    def setup(self, ok, json, text, headers):
        self._ok = ok
        self._json = json
        self._text = text
        self._headers = headers

    @property
    def ok(self):
        return self._ok

    def json(self):
        return self._json()

    @property
    def headers(self):
        return self._headers


def mock_ls120_pvoutput(*args, **kwargs) -> MockResponse:
    response = MockResponse()

    def raise_ex(e):
        raise Exception(e)

    if args[0] == '/e':
        response.setup(
            True,
            lambda: raise_ex("Unsupported operation"),
            'd=20210903&t=14:58&v1=3024759&v2=370&c1=1&v3=19623222&v4=300',
            {'Content-Type': 'text/html'})

    if args[0] == '/a?f=j':
        response.setup(
            True,
            lambda: {
                "cnt": " 16600,536",
                "pwr": -930,
                "lvl": 0,
                "dev": "",
                "det": "",
                "con": "OK",
                "sts": "(245)",
                "cs0": " 3021,525",
                "ps0": 1288,
                "raw": 0},
            '',
            {'Content-Type': 'application/json'})

    return response


class LS120Tests(unittest.TestCase):

    def test_ls120_failed(self):
        """Check what happens if the remote device is not ok"""
        with patch('youless_api.devices.requests.get') as mock_get:
            mock_get.return_value = Mock(ok=False)

            api = LS120('', {})
            api.update()

        self.assertEqual(api.state, STATE_FAILED)

    def test_ls120_ok(self):
        """Test the update functionality."""
        with patch('youless_api.devices.requests.get') as mock_get:
            mock_get.return_value = Mock(ok=True)
            mock_get.return_value.json.return_value = [{
                "tm": 1611929119,
                "net": 9194.164,
                "pwr": 2382,
                "ts0": 1608654000,
                "cs0": 0.000,
                "ps0": 0,
                "p1": 4703.562,
                "p2": 4490.631,
                "n1": 0.029,
                "n2": 0.000,
                "gas": 1624.264,
                "gts": int(datetime.datetime.now().strftime("%y%m%d%H00"))
            }]

            api = LS120('', {})
            api.update()

        self.assertEqual(api.state, STATE_OK)
        self.assertEqual(api.power_meter.total.value, 9194.164)
        self.assertEqual(api.power_meter.high.value, 4490.631)
        self.assertEqual(api.power_meter.low.value, 4703.562)
        self.assertEqual(api.current_power_usage.value, 2382)
        self.assertEqual(api.gas_meter.value, 1624.264)
        self.assertEqual(api.delivery_meter.high.value, 0.000)
        self.assertEqual(api.delivery_meter.low.value, 0.029)

    def test_ls120_gas_stale(self):
        """Test case for incident with stale data from the API"""
        with patch('youless_api.devices.requests.get') as mock_get:
            mock_get.return_value = Mock(ok=True)
            mock_get.return_value.json.return_value = [{
                "tm": 1611929119,
                "net": 9194.164,
                "pwr": 2382,
                "ts0": 1608654000,
                "cs0": 0.000,
                "ps0": 0,
                "p1": 4703.562,
                "p2": 4490.631,
                "n1": 0.029,
                "n2": 0.000,
                "gas": 1624.264,
                "gts": 3894900
            }]

            api = LS120('', {})
            api.update()

        self.assertEqual(api.state, STATE_OK)
        self.assertIsNone(api.gas_meter.value)

    def test_ls120_missing_p_and_n(self):
        """Test case for incident with missing sensors from the API"""
        with patch('youless_api.devices.requests.get') as mock_get:
            mock_get.return_value = Mock(ok=True)
            mock_get.return_value.json.return_value = [{
                "tm": 1611929119,
                "net": 9194.164,
                "pwr": 2382,
                "ts0": 1608654000,
                "cs0": 0.000,
                "ps0": 0,
                "gas": 1624.264,
                "gts": int(datetime.datetime.now().strftime("%y%m%d%H00"))
            }]

            api = LS120('', {})
            api.update()

        self.assertEqual(api.state, STATE_OK)
        self.assertEqual(api.power_meter.high.value, None)
        self.assertEqual(api.power_meter.low.value, None)

    @patch('youless_api.devices.requests.get', side_effect=mock_ls120_pvoutput)
    def test_ls120_pvoutput_firmware(self, mock_get):
        api = LS120PVOutput('', {})
        api.update()

        self.assertEqual(api.current_power_usage.value, -930)
        self.assertEqual(api.extra_meter.usage.value, 1288)
        self.assertEqual(api.extra_meter.total.value, " 3021,525")
        self.assertEqual(api.extra_meter.usage.value, 1288)


class LS110Test(unittest.TestCase):

    def test_ls110_ok(self):
        with patch('youless_api.devices.requests.get') as mock_get:
            mock_get.return_value = Mock(ok=True)
            mock_get.return_value.json.return_value = {
                "cnt": "141950,625",
                "pwr": 750,
                "lvl": 90,
                "dev": "(&plusmn;3%)",
                "det": "",
                "con": "OK",
                "sts": "(33)",
                "raw": 743
            }

            api = LS110('')
            api.update()

        self.assertEqual(api.state, STATE_OK)
        self.assertEqual(api.power_meter.high.value, None)
        self.assertEqual(api.power_meter.low.value, None)
        self.assertEqual(api.power_meter.total.unit_of_measurement, "kWh")
        self.assertEqual(api.power_meter.total.value, "141950,625")
        self.assertEqual(api.current_power_usage.value, 750)
