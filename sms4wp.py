#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import sys
import urllib
import urllib2
import poster


class Sms4wpClient(object):

    def __init__(self, _auth_email, _auth_token, _auth_digest, _url_root):

        self.auth_email = _auth_email
        self.auth_token = _auth_token
        self.auth_digest = _auth_digest
        self.url_root = _url_root

    def get_auth_header(self):
        return {"AUTHENTICATION": "token %s:%s" % (self.auth_email, self.auth_token)}

    def call_api(self, url, params, method, is_multipart):
        header = self.get_auth_header()

        if is_multipart:
            for k, v in params.items():
                if v[0] == '@':  # handle file macro
                    params[k] = open(v[1:], 'rb')

            poster.streaminghttp.register_openers()
            datagen, headers = poster.encode.multipart_encode(params)
            headers.update(header)
            code, res = self.send_request(url, datagen, headers, method.upper())

        else:
            data = urllib.urlencode(params) if params else None
            code, res = self.send_request(url, data, header, method.upper())

        return code, res

    def send_request(self, url, data, header, method):

        try:
            if method == 'GET':
                url += '?%s' % (data, ) if data else ''
                req = urllib2.Request(url, None, header)
            else:
                req = urllib2.Request(url, data, header)
                req.get_method = lambda: method

            print 'connecting to %s' % (url, )
            con = urllib2.urlopen(req)
            res = con.read()
            code = con.getcode()
            con.close()
            return code, res

        except urllib2.HTTPError as e:
            return e.code, e.read()

    def do_action(self, command, method, params):
        try:
            return self.__getattribute__('action_' + command)(method, params)
        except AttributeError:
            print >> sys.stderr, \
                "command '%s' for method '%s' is unimplemented, or unsupported API." % (command, method)
            sys.exit(1)

    def action_whoami(self, method, params):
        url = self.url_root + 'whoami/'
        return self.call_api(url=url, params=params, is_multipart=False, method=method)  # return code, json_text

    def action_test_task(self, method, params):
        url = self.url_root + 'test_task/'
        return self.call_api(url=url, params=params, is_multipart=False, method=method)

    def action_auth_token_grant(self, method, params):
        url = self.url_root + 'auth_token/grant/'
        return self.call_api(url=url, params=params, is_multipart=False, method=method)

    def action_auth_token_revoke(self, method, params):
        url = self.url_root + 'auth_token/revoke/'
        return self.call_api(url=url, params=params, is_multipart=False, method=method)

    def action_user_point(self, method, params):
        url = self.url_root + 'user_point/'
        return self.call_api(url=url, params=params, is_multipart=False, method=method)

    def action_auth_token(self, method, params):
        url = self.url_root + 'auth_token/'
        return self.call_api(url=url, params=params, is_multipart=False, method=method)

    def action_user(self, method, params):
        url = self.url_root + 'user/'
        return self.call_api(url=url, params=params, is_multipart=False, method=method)

    def action_transaction(self, method, params):
        url = self.url_root + 'transaction/'
        return self.call_api(url=url, params=params, is_multipart=False, method=method)

    def action_message(self, method, params):
        url = self.url_root + 'message/'

        if method == 'POST':
            if 'bulk_file' in params:
                return self.call_api(url=url, params=params, is_multipart=True, method=method)
            else:
                return self.call_api(url=url, params=params, is_multipart=False, method=method)

        if method == 'GET':
            return self.call_api(url=url, params=params, is_multipart=False, method=method)


def init():

    import argparse

    # argparser library: http://docs.python.org/2/library/argparse.html
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--command', metavar='CMD', type=unicode, nargs=1, help="Command. An API url.")
    parser.add_argument('-p', '--param', metavar="K:V", type=unicode, nargs='*', help="Parameters.")
    parser.add_argument('-f', '--file', type=unicode, nargs='*', help="JSON file form for calling API")
    parser.add_argument('-a', '--auth', type=unicode,
                        default='./auth_tokens.json', help="JSON file for authentication. DEFAULT: ./auth_tokens.json")
    parser.add_argument('-u', '--url-root', type=unicode,
                        default='http://backend.sms4wp.com/api/v0/',
                        help="Override API URL root. Put a slash at the end of string.")
    parser.add_argument('-m', '--method', type=unicode, default='GET', choices=['GET', 'POST', 'PUT', 'DELETE'],
                        help='Default: GET')

    args = parser.parse_args()

    del argparse

    return args


def do_file_commands(file_name):
    pass


def parse_params(param_list):

    params = dict()
    for item in param_list:
        if item[0] == '@':
            with open(item[1:], 'r') as f:
                params.update(json.load(f))
            for k, v in params.items():
                if isinstance(v, unicode):
                    params[k] = v.encode('utf-8')
        else:
            idx = item.find(':')
            k = item[:idx].strip()
            v = item[idx+1:].strip()
            params[k] = v

    # utf-8 encode plz
    print 'params:', params
    return params


def main():
    args = init()
    params = None

    with open(args.auth, 'r') as f:
        import json
        json_object = json.load(f)
        auth_email = json_object['auth_email']
        auth_token = json_object['auth_token']
        auth_digest = json_object['auth_digest']
        del json

    if args.file:
        do_file_commands(args.file)

    if args.param:
        params = parse_params(args.param)

    if args.command:
        command = args.command[0]
        method = args.method

        client = Sms4wpClient(auth_email, auth_token, auth_digest, _url_root=args.url_root)
        code, json_text = client.do_action(command, method, params)

        print 'server response: %s' % (code, )
        print 'JSON text: %s' % (json_text, )

    return 0

if __name__ == '__main__':
    sys.exit(main())
