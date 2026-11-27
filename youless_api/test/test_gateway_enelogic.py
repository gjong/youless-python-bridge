from datetime import datetime
from unittest import TestCase
from unittest.mock import patch, Mock, MagicMock

from requests import Response

from youless_api.gateway import fetch_enologic_api


def mock_ls120_ok(*args, **kwargs) -> Response:
    if args[0] == 'http://localhost/e':
        return Mock(
            ok=True,
            headers={'Content-Type': 'application/json'},
            json=lambda: [{
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
        )

    return Mock(ok=False)


def mock_stale_gas(*args, **kwargs) -> Response:
    if args[0] == 'http://localhost/e':
        return Mock(
            ok=True,
            headers={'Content-Type': 'application/json'},
            json=lambda: [{
                "tm": 1611929119,
                "net": 9194.164,
                "pwr": 2382,
                "ts0": 1608654000,
                "cs0": 15.000,
                "ps0": 10,
                "p1": 4703.562,
                "p2": 4490.631,
                "n1": 0.029,
                "n2": 0.000,
                "gas": 1624.264,
                "gts": 3894900,
                "wtr": 1234.564,
                "wts": 3894900
            }]
        )

    return Mock(ok=False)


def mock_enologic_missing_values(*args, **kwargs) -> Response:
    if args[0] == 'http://localhost/e':
        return Mock(
            ok=True,
            headers={'Content-Type': 'application/json'},
            json=lambda: [{
                "tm": 1611929119,
                "net": 9194.164,
                "pwr": 2382,
                "ts0": 1608654000,
                "cs0": 0.000,
                "ps0": 0,
                "gas": 1624.264,
                "gts": int(datetime.now().strftime("%y%m%d%H00")),
                "wtr": 1234.564,
                "wts": int(datetime.now().strftime("%y%m%d%H00"))
            }]
        )

    return Mock(ok=False)


def mock_enologic_error(*args, **kwargs) -> Response:
    return Mock(ok=False)


class GatewayTest(TestCase):

    @patch('youless_api.gateway.datetime')
    @patch('youless_api.gateway.requests.get')
    def test_enologic_recent_gas_from_previous_day_is_not_stale(
            self, mock_get: MagicMock, mock_datetime: MagicMock):
        mock_datetime.now.return_value = datetime(2026, 11, 27, 0, 1)
        mock_datetime.strptime.side_effect = datetime.strptime
        mock_get.return_value = Mock(
            ok=True,
            headers={'Content-Type': 'application/json'},
            json=lambda: [{
                "gas": 1624.264,
                "gts": 2611262359,
                "wtr": 1234.564,
                "wts": 2611262359
            }]
        )

        dataset = fetch_enologic_api('localhost', None)

        self.assertEqual(dataset['gas'], 1624.264)
        mock_get.assert_called_once_with('http://localhost/e', auth=None, timeout=2)

    @patch('youless_api.gateway.requests.get')
    def test_enologic_invalid_timestamp_is_stale(self, mock_get: MagicMock):
        mock_get.return_value = Mock(
            ok=True,
            headers={'Content-Type': 'application/json'},
            json=lambda: [{
                "gas": 1624.264,
                "gts": 2613320000,
                "wtr": 1234.564,
                "wts": 0
            }]
        )

        dataset = fetch_enologic_api('localhost', None)

        self.assertIsNone(dataset['gas'])
        self.assertEqual(dataset['wtr'], 1234.564)

    @patch('youless_api.gateway.requests.get', side_effect=mock_ls120_ok)
    def test_enologic_correct(self, mock_get: MagicMock):
        dataset = fetch_enologic_api('localhost', None)

        self.assertEqual(dataset['net'], 9194.164)
        self.assertEqual(dataset['p2'], 4490.631)
        self.assertEqual(dataset['p1'], 4703.562)
        self.assertEqual(dataset['pwr'], 2382)
        self.assertEqual(dataset['gas'], 1624.264)
        self.assertEqual(dataset['wtr'], 1234.564)
        self.assertEqual(dataset['cs0'], 0.000)
        self.assertEqual(dataset['n1'], 0.029)
        mock_get.assert_any_call('http://localhost/e', auth=None, timeout=2)

    @patch('youless_api.gateway.requests.get', side_effect=mock_stale_gas)
    def test_enologic_stale_gas(self, mock_get: MagicMock):
        dataset = fetch_enologic_api('localhost', None)

        self.assertEqual(dataset['net'], 9194.164)
        self.assertEqual(dataset['p2'], 4490.631)
        self.assertEqual(dataset['p1'], 4703.562)
        self.assertEqual(dataset['pwr'], 2382)
        self.assertEqual(dataset['gas'], None)
        self.assertEqual(dataset['wtr'], None)
        self.assertEqual(dataset['cs0'], 15.000)
        self.assertEqual(dataset['ps0'], 10)
        self.assertEqual(dataset['n1'], 0.029)
        mock_get.assert_any_call('http://localhost/e', auth=None, timeout=2)

    @patch('youless_api.gateway.requests.get', side_effect=mock_enologic_missing_values)
    def test_enologic_missing_p_and_n(self, mock_get: MagicMock):
        dataset = fetch_enologic_api('localhost', None)

        self.assertEqual(dataset['p1'], None)
        self.assertEqual(dataset['p2'], None)
        self.assertEqual(dataset['n1'], None)
        self.assertEqual(dataset['n2'], None)
        mock_get.assert_any_call('http://localhost/e', auth=None, timeout=2)

    @patch('youless_api.gateway.requests.get', side_effect=mock_enologic_error)
    def test_enologic_error(self, mock_get: MagicMock):
        dataset = fetch_enologic_api('localhost', None)

        self.assertEqual(dataset, None)
        mock_get.assert_any_call('http://localhost/e', auth=None, timeout=2)

