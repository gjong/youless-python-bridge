"""
This file contains a helper class to easily obtain data from the YouLess sensor.
"""

import json
from urllib.request import urlopen

name = "youless_pyhton_bridge"


class YoulessData:
    """A wrapper class to contain the Youless Sensor values"""

    def __init__(self, value, uom):
       """Initialize the value wrapper"""
       self._value = value
       self._uom = uom

    def unit_of_measurement(self):
       """Get the unit of measurement for this value"""
       return self._uom

    def value(self):
       """Get the current value"""
       return self._value


class YoulessDataBridge:
    """A helper class to obtain data from the YouLess Sensor"""

    def __init__(self, host):
        """Initialize the data bridge"""
        self._url = 'http://' + host + '/e'
        self._cache = None

    def update(self):
        """Fetch the latest settings from the Youless Sensor"""
        raw_json = urlopen(self_url)
        self._cache = json.loads(raw_json.read().decode('utf-8'))[0]

    def gas_meter(self): 
        """"Get the gas data available"""
        if self._cache is not None:
           return YoulessData(self._cache['gas'], 'm3')

        return None

    def current_power_usage(self):
        """Get the current power usage"""
        if self._cache is not None:
           return YoulessData(self._cache['pwr'], 'kW')
        
        return None

    def power_meter(self):
        """Get the power meter values"""
        if self._cache is not None:
           return {
              'total': YoulessData(self._cache['net'], 'kWh'),
              'low': YoulessData(self._cache['p1'], 'kWh'),
              'high': YoulessData(self._cache['p2'], 'kWh')
           }

        return None

    def delivery_meter(self):
        """Get the power delivered values"""
        if self._cache is not None:
           return {
              'low': YoulessData(self._cache['n1'], 'kWh'),
              'high': YoulessData(self._cache['n2'], 'kWh')
           }

        return None

    def exta_meter(self):
        """Get the meter values of an attached meter"""
        if self._cache is not None:
           return {
               'total': YoulessData(self._cache['cs0'], 'kWh'),
               'current': YoulessData(self._cache['ps0'], 'kWh')
           }

        return None

