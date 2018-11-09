from setuptools import setup

setup(name='youless_python_bridge',
      version='0.1',
      description='A bridge for python to the YouLess sensor',
      url='https://bitbucket.org/jongsoftdev/youless-python-bridge/src/master/',
      author='G. Jongerius',
      license='MIT',
      test_suite='nose.collector',
      tests_require=['nose'],
      packages=['youless_python_bridge'],
      zip_safe=False)
