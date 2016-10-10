# bpapi
Python client library for BrightPattern List API

To install from GitHub:
```
pip install git+https://github.com/filindm/bpapi.git
```
Example of usage:
```python
from bpapi import BpListApi

api = BpListApi(
  hostname="<your hostname>", 
  tenant="<your tenant url>", 
  login="<login>", 
  password="<password>", 
  ssl=True)
for c in api.get_campaigns():
    print c
```
