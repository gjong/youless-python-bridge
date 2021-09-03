import unittest
from unittest.mock import patch, Mock, MagicMock

from requests import Response

from youless_api import YoulessAPI


def mock_ls110_device(*args, **kwargs) -> Mock:
    ok_status = False

    if args[0] == 'http://192.1.1.1':
        ok_status = True

    return Mock(
        ok=ok_status,
        return_value='{}')


def mock_ls120_device(*args, **kwargs) -> Response:
    response = Mock(ok=False)

    if args[0] == 'http://192.1.1.1/d':
        response.ok = True

    response.return_value.json.return_value = {'mac': '293:23fd:23'}

    return response


class YoulessAPITest(unittest.TestCase):

    @patch('youless_api.requests.get', side_effect=mock_ls120_device)
    def test_device_ls120(self, mock_get: MagicMock):
        api = YoulessAPI('192.1.1.1')
        api.initialize()

        self.assertEqual(api.model, 'LS120')
        self.assertEqual(api.mac_address, '293:23fd:23')

        mock_get.assert_called_with('http://192.1.1.1/d', auth=None)

    @patch('youless_api.requests.get', side_effect=mock_ls110_device)
    def test_device_ls110(self, mock_get: MagicMock):
        api = YoulessAPI('192.1.1.1')
        api.initialize()

        self.assertEqual(api.model, 'LS110')
        self.assertIsNone(api.mac_address)

        mock_get.assert_called_with('http://192.1.1.1', auth=None)
