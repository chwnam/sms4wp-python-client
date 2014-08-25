#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import urllib
import urllib2
import poster


class Sms4wpClient(object):

    url_root = 'http://backend.sms4wp.com/api/v0/'

    def __init__(self, _auth_email, _auth_token, _auth_digest):

        self.auth_email = _auth_email
        self.auth_token = _auth_token
        self.auth_digest = _auth_digest

    def get_auth_header(self):
        return {"AUTHENTICATION": "token %s:%s" % (self.auth_email, self.auth_token)}

    def call_api(self, url, params, is_multipart):
        header = self.get_auth_header()

        if is_multipart:
            for k, v in params:
                if v[0] == '@':  # handle file macro
                    params[k] = open(v[1:], 'rb')

            poster.streaminghttp.register_openers()
            datagen, headers = poster.encode.multipart_encode(params)
            headers = dict(headers, header)
            code, res = self.send_request(url, datagen, headers)

        else:
            data = urllib.urlencode(params) if params else None
            code, res = self.send_request(url, data, header)

        return code, res

    def send_request(self, url, data, header):
        try:
            req = urllib2.Request(url, data, header)
            con = urllib2.urlopen(req)
            res = con.read()
            code = con.getcode()
            con.close()
            return code, res

        except urllib2.HTTPError as e:
            return e.code, e.read()

    def do_action(self, command, params):
        try:
            return self.__getattribute__(command)(params)
        except AttributeError as e:
            print >> sys.stderr, "command '%s' is unimplemented, or unsupported API." % (command, )
            sys.exit(1)

    def whoami(self, params):
        url = self.__class__.url_root + 'whoami/'
        return self.call_api(url=url, params=params, is_multipart=False)  # return code, json_text

    def point(self, params):
        url = self.__class__.url_root + 'point/'
        return self.call_api(url=url, params=params, is_multipart=False)


def init():

    import argparse

    # argparser library: http://docs.python.org/2/library/argparse.html
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--command', metavar='CMD', type=unicode, nargs=1, help="Command. An API url.")
    parser.add_argument('-p', '--param', metavar="K:V", type=unicode, nargs='*', help="Parameters.")
    parser.add_argument('-f', '--file', type=unicode, nargs='*', help="JSON file form for calling API")
    parser.add_argument('-a', '--auth', type=unicode,
                        default='./auth_tokens.json', help="JSON file for authentication. DEFAULT: ./auth_tokens.json")
    args = parser.parse_args()

    del argparse

    return args


def do_file_commands(file_name):
    pass


def parse_params(param_list):
    params = dict()
    for item in param_list:
        k, v = item.split(':')
        params[k] = v
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
        client = Sms4wpClient(auth_email, auth_token, auth_digest)
        code, json_text = client.do_action(command, params)

        print 'server response: %s' % (code, )
        print 'JSON text: %s' % (json_text, )

    return 0

if __name__ == '__main__':
    sys.exit(main())
