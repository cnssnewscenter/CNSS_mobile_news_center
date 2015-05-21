import tornado.httpclient
import redis
import tornado.httpclient
from tornado.options import options
import tornado.gen
from tornado.log import logging

try:
    # try to connect to the server
    # if success, use cache,
    # else disable success
    r = redis.Redis()
    caching = True
except Exception as e:
    print(e)
    caching = False
    r = ""
    logging.warn('Due to %s, can not connect to the redis and disable caching\n Please check.', e)


@tornado.gen.coroutine
def get_page(url):
    """
    Cache enabled page fetching
    """
    if caching:
        cached = r.get(url)
        if cached:
            return cached
    client = tornado.httpclient.AsyncHTTPClient()
    result = yield client.fetch(url)
    if 300 >= result.code >= 200:
        r.setex(url, result.body, options.CACHE_TIME)
    return result.body
