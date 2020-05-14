# DBLAuthV1.py

# This is the authorization class for accessing DBL

try:
        from requests.auth import AuthBase
except ImportError as ex:
        AuthBase = None  # declare AuthBase to silence pep8 warnings
        if __name__ != "__main__":
                raise Exception('cannot import requests module')


class DBLAuthV1(AuthBase):
#class DBLAuthV1:
        authorization_header = 'X-DBL-Authorization'

        def __init__(self, api_token, private_key):
                super(DBLAuthV1, self).__init__()
                self.api_token = api_token.lower()
                self.private_key = private_key.lower()

        def __call__(self, r):
                r.headers[self.authorization_header] = self.make_authorization_header(r)
                return r

        def make_authorization_header(self, request):
                import hmac
                import hashlib

                mac = hmac.new(self.api_token, None, hashlib.sha1)
                mac.update(self.signing_string_from_request(request))
                mac.update(self.private_key.lower())
                return 'version=v1,token=%s,signature=%s' % (self.api_token, mac.hexdigest().lower())

        def signing_string_from_request(self, request):
                dbl_header_prefix = 'x-dbl-'
                signing_headers = ['content-type', 'date']

                method = request.method
                # use request uri, but not any of the arguments.
                path = request.path_url.split('?')[0]
                collected_headers = {}

                for key, value in request.headers.iteritems():
                        if key == self.authorization_header:
                                continue
                        k = key.lower()
                        if k in signing_headers or k.startswith(dbl_header_prefix):
                                collected_headers[k] = value.strip()

                # these keys get empty strings if they don't exist
                if 'content-type' not in collected_headers:
                        collected_headers['content-type'] = ''
                if 'date' not in collected_headers:
                        collected_headers['date'] = ''

                sorted_header_keys = sorted(collected_headers.keys())

                buf = "%s %s\n" % (method, path)
                for key in sorted_header_keys:
                        val = collected_headers[key]
                        if key.startswith(dbl_header_prefix):
                                buf += "%s:%s\n" % (key, val)
                        else:
                                buf += "%s\n" % val
                return buf


if __name__ == "__main__":
        import requests
        from datetime import datetime
        from wsgiref.handlers import format_date_time
        from time import mktime
        from Config import *
        config = Config()

        #auth = DBLAuthV1('60AD09DFA8126695262F',
        #    '768FA670E21B6AE949891EE74FFC94A2BD16DFBFF4C074621101F99696065CC9C9C557788B6335C7')
        auth = DBLAuthV1('4F945541A4AD1F363F8D', b'CA643B967D66526875AEACBDED46C3BDAC8EB84D594BF6FBA6DD9BA781A96E314D56E0BBEEAF707B')
        #auth = DBLAuthV1(config.DBL_MY_TOKEN, config.DBL_MY_SECRET)
        baseURL = "https://thedigitalbiblelibrary.org/api/"
        #response = requests.get('http://localhost:8000/api/orgs', auth=auth,
        response = requests.get(baseURL + "orgs", auth=auth,
            headers={'Date': format_date_time(mktime(datetime.now().timetuple())),
                     'Content-Type': 'application/json'})
        print(response.status_code)

