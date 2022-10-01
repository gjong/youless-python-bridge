import datetime
from typing import Optional

import requests

from youless_api.const import STATE_OK, STATE_FAILED
from youless_api.device import YouLessDevice
from youless_api.youless_sensor import YoulessSensor, PowerMeter, ExtraMeter, DeliveryMeter


def validate_enologic_response(raw_data: dict) -> dict:
    """Validate the response to verify that it makes sense and no junk data is returned"""

    corrected = {**{'p1': None, 'p2': None, 'n1': None, 'n2': None, 'gas': None}, **raw_data}
    if 'gts' in corrected:
        formatted_date = datetime.datetime.now().strftime("%y%m%d") + "0000"
        if corrected["gts"] != 0 and int(formatted_date) >= corrected["gts"]:
            corrected["gas"] = None

    return corrected


class LS120(YouLessDevice):
    """The device integration for the Youless LS120"""

    def __init__(self, host, device_information):
        """Initialize the integration"""
        super().__init__()
        self._host = host
        self._cache = None
        self._state = STATE_OK
        self._info = device_information

    @property
    def gas_meter(self):
        """"Get the gas meter from the internal cache"""
        if self._cache is not None:
            return YoulessSensor(self._cache['gas'], 'm3')

        return None

    @property
    def current_power_usage(self):
        """Get the current power usage from the internal cache"""
        if self._cache is not None:
            return YoulessSensor(self._cache['pwr'], 'W')

        return None

    @property
    def power_meter(self):
        """Get the power meter values."""
        if self._cache is not None:
            return PowerMeter(
                YoulessSensor(self._cache['p1'], 'kWh'),
                YoulessSensor(self._cache['p2'], 'kWh'),
                YoulessSensor(self._cache['net'], 'kWh')
            )

        return None

    @property
    def delivery_meter(self):
        """Get the power delivered values."""
        if self._cache is not None:
            return DeliveryMeter(
                YoulessSensor(self._cache['n1'], 'kWh'),
                YoulessSensor(self._cache['n2'], 'kWh')
            )

        return None

    @property
    def extra_meter(self):
        """Get the meter values of an attached meter."""
        if self._cache is not None:
            return ExtraMeter(
                YoulessSensor(self._cache['cs0'], 'kWh'),
                YoulessSensor(self._cache['ps0'], 'W')
            )

        return None

    @property
    def state(self) -> Optional[str]:
        """Returns the current connectivity state"""
        return self._state

    @property
    def mac_address(self) -> Optional[str]:
        """Return the MAC address"""
        if self._info is not None:
            return self._info['mac']

        return None

    @property
    def model(self) -> Optional[str]:
        """Return the device model"""
        return "LS120"

    def update(self) -> None:
        """Update the sensor values from the device"""
        response = requests.get(f"{self._host}/e", timeout=2)
        if response.ok:
            response = validate_enologic_response(response.json()[0])
            if response is not None:
                self._state = STATE_OK
                self._cache = response
            else:
                self._state = STATE_FAILED
        else:
            self._state = STATE_FAILED