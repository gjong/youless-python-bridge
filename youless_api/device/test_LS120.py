import datetime
from unittest import TestCase
from unittest.mock import patch, Mock

from youless_api.const import STATE_FAILED, STATE_OK
from youless_api.device.LS120 import LS120


class LS120Tests(TestCase):

    def test_ls120_failed(self):
        """Check what happens if the remote device is not ok"""
        with patch('youless_api.device.LS120.requests.get') as mock_get:
            mock_get.return_value = Mock(ok=False)

            api = LS120('', {})
            api.update()

        self.assertEqual(api.state, STATE_FAILED)

    def test_ls120_ok(self):
        """Test the update functionality."""
        with patch('youless_api.device.LS120.requests.get') as mock_get:
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
        with patch('youless_api.device.LS120.requests.get') as mock_get:
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
        with patch('youless_api.device.LS120.requests.get') as mock_get:
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
