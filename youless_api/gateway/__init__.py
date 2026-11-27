from datetime import datetime, timedelta
from typing import Optional

import requests


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

        if corrected.get("gts") not in (None, 0):
            gas_timestamp = datetime.strptime(str(corrected['gts']), "%y%m%d%H%M")
            if datetime.now() - gas_timestamp > timedelta(hours=2):
                corrected["gas"] = None

        if corrected.get("wts") not in (None, 0):
            water_timestamp = datetime.strptime(str(corrected['wts']), "%y%m%d%H%M")
            if datetime.now() - water_timestamp > timedelta(hours=2):
                corrected["wts"] = None

        return corrected

    return None


def fetch_device_info(host, authentication=None) -> Optional[dict]:
    """Fetch the device information from the Youless device."""
    response = requests.get(f"http://{host}/d", auth=authentication, timeout=2)

    return response.json() if response.ok else None
