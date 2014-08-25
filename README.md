sms4wp-python-client
====================

sms4wp.com API client python script.

## How to Use
Create a json file named 'auth_tokens.json' in a directory where sms4wp.py script is.
This file contains an object which has three key-value pairs: 'auth_token', 'auth_digest', 'auth_email'

```
{
    "auth_email": "",
    "auth_token": "",
    "auth_digest": ""
}
```

This code depends on [poster](https://pypi.python.org/pypi/poster/) library. To install,
```bash
pip install poster
```
in a terminal.


## Currently Supported API call ##

### whoami
#### usage
  ./sms4wp.py -c whoami
