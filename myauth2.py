# -*- coding: utf-8 -*-

from weibo import APIClient
import urllib, urllib2, cookielib
import urlparse
import time

__version__ = '0.1'
__author__ = 'Anqi Cui (caq@caq9.info)'

'''
My OAuth 2.0 authentication processes
Store the keys in a file. If it expires, automatically renew.
Usage:
from myauth2 import MyAuth2
ma2 = MyAuth2('your app key')
print ma2.client.post.statuses__update(status='Hello, Weibo!')
'''

class MyAuth2:
    APP_KEY = None
    APP_SECRET = None
    CALLBACK_URL = None
    ACCESS_TOKEN = None
    EXPIRES_IN = None
    client = None
    USERNAME = None
    PASSWORD = None

    # constructor. App info should be provided.
    def __init__(self, key, secret=None, callback=None, filename=None, username=None, password=None):
        self.APP_KEY = key
        if secret is None: # read everything from file
            if filename is None:
                filename = str(key) + '.token'
            f = open(filename)
            for line in f.readlines():
                parts = line.strip().split('\t')
                # key, secret, url, token, expire, username, password
                if cmp(parts[0], str(key)) == 0:
                    self.APP_SECRET = parts[1]
                    self.CALLBACK_URL = parts[2]
                    self.ACCESS_TOKEN = parts[3]
                    self.EXPIRES_IN = float(parts[4])
                    self.USERNAME = parts[5]
                    self.PASSWORD = parts[6]
                    break
            f.close()
        else: # read from input. check if file exists and has other things
            self.APP_SECRET = secret
            self.CALLBACK_URL = callback
            if filename is not None:
                f = open(filename)
                for line in f.readlines():
                    parts = line.strip().split('\t')
                    # key, secret, url, token, expire, username, password
                    if cmp(parts[0], str(key)) == 0:
                        self.APP_SECRET = parts[1]
                        self.CALLBACK_URL = parts[2]
                        self.ACCESS_TOKEN = parts[3]
                        self.EXPIRES_IN = float(parts[4])
                        self.USERNAME = parts[5]
                        self.PASSWORD = parts[6]
                        break
                f.close()
        if username is not None:
            self.USERNAME = username
        if password is not None:
            self.PASSWORD = password
        if self.EXPIRES_IN == None or time.time() >= self.EXPIRES_IN: # need to authenticate again
            url = self.getURL()
            code = self.getCode(url, self.USERNAME, self.PASSWORD)
            self.getToken(code)
            self.store()
        else:
            self.client = APIClient(app_key=self.APP_KEY, app_secret=self.APP_SECRET, redirect_uri=self.CALLBACK_URL)
            self.client.set_access_token(self.ACCESS_TOKEN, self.EXPIRES_IN)


    # first step, get the url
    def getURL(self, display='wap2.0'):
        self.client = APIClient(app_key=self.APP_KEY, app_secret=self.APP_SECRET, redirect_uri=self.CALLBACK_URL)
        url = self.client.get_authorize_url(display=display)
        return url

    # use the url to authenticate
    def getCode(self, url, username, password):
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(MyHTTPRedirectHandler, urllib2.HTTPCookieProcessor(cj))
        opener.addheaders = [('User-Agent', 'Opera/9.80 (J2ME/MIDP; Opera Mini/4.0/886; U; en) Presto/2.4.15'), ('Host', 'api.weibo.com'), ('Referer', url)]
        urllib2.install_opener(opener)
        # open the login page
        req = urllib2.Request(url)
        conn = urllib2.urlopen(req)

        # fill in the forms and submit (POST)
        parseresult = urlparse.urlparse(url)
        querystring = urlparse.parse_qs(parseresult.query)
        for key in querystring:
            querystring[key] = querystring[key][0]
        querystring['action'] = 'submit'
        querystring['userId'] = username
        querystring['passwd'] = password
        post_data = urllib.urlencode(querystring)
        req = urllib2.Request('https://api.weibo.com/oauth2/authorize')
        location = urllib2.urlopen(req, data=post_data)
        code = urlparse.parse_qs(urlparse.urlparse(location).query)
        code = code['code'][0]
        return code

    # use the code from the webpage authentication to get tokens
    def getToken(self, code):
        #code = raw_input('PIN: ').strip()
        r = self.client.request_access_token(code)
        self.ACCESS_TOKEN = r.access_token # access token
        self.EXPIRES_IN = r.expires_in # UNIX time of the token expiration time
        #print access_token, expires_in
        self.client.set_access_token(self.ACCESS_TOKEN, self.EXPIRES_IN)
        return {'access_token':self.ACCESS_TOKEN, 'expires_in':self.EXPIRES_IN}

    # store to disk
    def store(self, filename=None):
        if filename is None:
            filename = str(self.APP_KEY) + '.token'
        fw = open(filename, 'w')
        fw.write(str(self.APP_KEY) + '\t' + self.APP_SECRET + '\t' + self.CALLBACK_URL + '\t' + str(self.ACCESS_TOKEN) + '\t' + str(self.EXPIRES_IN) + '\t' + self.USERNAME + '\t' + self.PASSWORD + '\n')
        fw.close()

# This class handles redirection. Instead of returning the default 
#   handler, I return the new location only as a str.
class MyHTTPRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        return headers['Location']
        #return urllib2.HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)

    http_error_301 = http_error_303 = http_error_307 = http_error_302
