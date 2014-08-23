sms4wp-python-client
====================

sms4wp.com API client python script.

## How to Use
Just assign values to auth_email, auth_token, auth_digest global variables in the top of sms4wp.py code.

This code depends on [poster](https://pypi.python.org/pypi/poster/) library. To install,
```bash
pip install poster
```
in a terminal.


## Currently Supported API call ##

### whoami
#### usage
  ./sms4wp.py -c whoami
