from datetime import datetime, timedelta
from typing import Optional

import requests


def _is_stale_timestamp(timestamp):
    if timestamp in (None, 0):
        return False

    timestamp = str(timestamp)
    if len(timestamp) != 10 or not timestamp.isdigit():
        return True

    try:
        timestamp = datetime.strptime(timestamp, "%y%m%d%H%M")
    except ValueError:
        return True

    return datetime.now() - timestamp > timedelta(hours=2)


def fetch_generic_api(host, authentication=None) -> Optional[dict]:
    """Fetches the data from the Youless API on the /a endpoint."""
    response = requests.get(f"http://{host}/a?f=j", auth=authentication, timeout=2)

    if response.ok:
        corrected = {**{'cs0': None, 'ps0': None}, **response.json()}
        parse_float_values_for = ['cnt', 'cs0']

        for correct_value in parse_float_values_for:
            if correct_value in corrected and corrected[correct_value] is not None:
                corrected[correct_value] = float(corrected[correct_value].replace(",", "."))

        return corrected

    return None


def fetch_phase_api(host, authentication=None) -> Optional[dict]:
    """Fetches the data from the Youless API on the /f endpoint."""
    response = requests.get(f"http://{host}/f", auth=authentication, timeout=2)

    return response.json() if response.ok else {}


def fetch_enologic_api(host, authentication=None):
    """Fetches the data from the Youless API on the /e endpoint."""
    response = requests.get(f"http://{host}/e", auth=authentication, timeout=2)

    if response.ok and response.headers['Content-Type'] == 'application/json':
        """Use fallback values if specific sensor values are missing."""
        corrected = {
            **{
                'p1': None,
                'p2': None,
                'n1': None,
                'n2': None,
                'gas': None,
                'wtr': None,
                'pwr': None,
                'cs0': None,
                'ps0': None},
            **response.json()[0]
        }

        if _is_stale_timestamp(corrected.get("gts")):
            corrected["gas"] = None

        if _is_stale_timestamp(corrected.get("wts")):
            corrected["wtr"] = None

        return corrected

    return None


def fetch_device_info(host, authentication=None) -> Optional[dict]:
    """Fetch the device information from the Youless device."""
    response = requests.get(f"http://{host}/d", auth=authentication, timeout=2)

    return response.json() if response.ok else None
