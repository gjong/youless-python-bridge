# YouLess Python Data Bridge
[![PyPI version](https://badge.fury.io/py/youless-python-bridge.svg)](https://badge.fury.io/py/youless-python-bridge)

This package contains support classes to fetch data from the YouLess sensors.

To use the API use the following code:

```python

from youless_api.youless_api import YoulessAPI

if __name__ == '__main__':
    api = YoulessAPI("192.168.1.2")  # use the ip address of the youless device
    api.update()

    gasUsage = api.gas_meter.value

```