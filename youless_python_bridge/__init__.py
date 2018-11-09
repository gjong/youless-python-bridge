"""
This file contains a helper class to easily obtain data from the YouLess sensor.
"""
import json
from urllib.request import urlopen

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
        if self._cache is not None
           return self._cache['gas']
