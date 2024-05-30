import unittest
from datetime import datetime
from unittest.mock import patch, Mock, MagicMock

from requests import Response

from youless_api import YoulessAPI

test_host = "192.1.1.1"


def mock_ls120_pvoutput(*args, **kwargs) -> Response:
    response: Response = Mock()

    if args[0] == 'http://192.1.1.1/d':
        response.ok = True
        response.json = lambda: {'mac': '293:23fd:23'}

    if args[0] == 'http://192.1.1.1/e':
        response.ok = True
        response.headers = {'Content-Type': 'text/html'}

    if args[0] == 'http://192.1.1.1/a?f=j':
        return Mock(
            ok=True,
            json=lambda: {
                "cnt": "141950,625",
                "pwr": 750,
                "lvl": 90,
                "dev": "(&plusmn;3%)",
                "det": "",
                "con": "OK",
                "sts": "(33)",
                "raw": 743
            })

    return response


def mock_ls120(*args, **kwargs) -> Response:
    response: Response = Mock()

    if args[0] == 'http://192.1.1.1/d':
        response.ok = True
        response.json = lambda: {'mac': '293:23fd:23'}

    if args[0] == 'http://192.1.1.1/e':
        response.ok = True
        response.headers = {'Content-Type': 'application/json'}
        response.json = lambda: [{
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
            "gts": int(datetime.now().strftime("%y%m%d%H00")),
            "wtr": 1234.564,
            "wts": int(datetime.now().strftime("%y%m%d%H00"))
        }]

    return response


def mock_ls110_device(*args, **kwargs):
    if args[0] == 'http://192.1.1.1/d':
        return Mock(ok=False)
    if args[0] == 'http://192.1.1.1/a?f=j':
        return Mock(
            ok=True,
            json=lambda: {
                "cnt": "141950,625",
                "pwr": 750,
                "lvl": 90,
                "dev": "(&plusmn;3%)",
                "det": "",
                "con": "OK",
                "sts": "(33)",
                "raw": 743
            })

    return Mock(ok=False)


class YoulessAPITest(unittest.TestCase):

    @patch('youless_api.gateway.requests.get', side_effect=mock_ls120)
    def test_device_ls120(self, mock_get: MagicMock):
        api = YoulessAPI(test_host)
        api.initialize()
        api.update()

        self.assertEqual(api.model, 'LS120')
        self.assertEqual(api.mac_address, '293:23fd:23')
        mock_get.assert_any_call('http://192.1.1.1/d', auth=None, timeout=2)
        mock_get.assert_any_call('http://192.1.1.1/e', auth=None, timeout=2)

    @patch('youless_api.gateway.requests.get', side_effect=mock_ls120)
    def test_device_ls120_authenticated(self, mock_get: MagicMock):
        api = YoulessAPI(test_host, 'admin', 'password')
        api.initialize()

        self.assertEqual(api.model, 'LS120')
        mock_get.assert_any_call('http://192.1.1.1/d', auth=('admin', 'password'), timeout=2)
        mock_get.assert_any_call('http://192.1.1.1/e', auth=('admin', 'password'), timeout=2)

    @patch('youless_api.gateway.requests.get', side_effect=mock_ls120_pvoutput)
    def test_ls120_firmare_pvoutput(self, mock_get: MagicMock):
        api = YoulessAPI(test_host)
        api.initialize()
        api.update()

        self.assertEqual(api.model, 'LS120 - PVOutput')
        self.assertEqual(api.mac_address, '293:23fd:23')
        mock_get.assert_any_call('http://192.1.1.1/d', auth=None, timeout=2)
        mock_get.assert_any_call('http://192.1.1.1/e', auth=None, timeout=2)

    @patch('youless_api.gateway.requests.get', side_effect=mock_ls120_pvoutput)
    def test_ls120_firmare_pvoutput_authenticated(self, mock_get: MagicMock):
        api = YoulessAPI(test_host, 'admin', 'password')
        api.initialize()

        self.assertEqual(api.model, 'LS120 - PVOutput')
        self.assertEqual(api.mac_address, '293:23fd:23')
        mock_get.assert_any_call('http://192.1.1.1/d', auth=('admin', 'password'), timeout=2)
        mock_get.assert_any_call('http://192.1.1.1/e', auth=('admin', 'password'), timeout=2)

    @patch('youless_api.gateway.requests.get', side_effect=mock_ls110_device)
    def test_device_ls110(self, mock_get: MagicMock):
        api = YoulessAPI(test_host)
        api.initialize()

        mock_get.assert_called_with('http://192.1.1.1/d', auth=None, timeout=2)
        self.assertEqual(api.model, 'LS110')
        self.assertIsNone(api.mac_address)

        api.update()
        mock_get.assert_called_with('http://192.1.1.1/a?f=j', auth=None, timeout=2)

    @patch('youless_api.gateway.requests.get', side_effect=mock_ls110_device)
    def test_device_ls110_authenticated(self, mock_get: MagicMock):
        api = YoulessAPI(test_host, 'admin', 'password')
        api.initialize()
        mock_get.assert_called_with('http://192.1.1.1/d', auth=('admin', 'password'), timeout=2)

        self.assertEqual(api.model, 'LS110')
        self.assertIsNone(api.mac_address)
