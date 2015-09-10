import tornado.httpclient
import redis
from tornado.options import options
import tornado.gen
from tornado.log import logging
from tornado.options import options


r = redis.Redis()
caching = True


@tornado.gen.coroutine
def get_data(key):
    """
    return None or the data in the redis cache
    """
    global caching
    if caching:
        try:
            cached = r.get(key)
            return cached.decode()
        except:
            logging.warn('Fail to connect to the redis cache server')
            caching = False
            return None
    else:
        return None


@tornado.gen.coroutine
def write_data(key, value, timeout):
    global r, caching
    if caching:
        try:
            r.setex(key, value, timeout)
        except:
            caching = False
            logging.warn('Fail to connect to the redis cache server')


@tornado.gen.coroutine
def get_page(url):
    """
    Cache enabled page fetching
    """
    cached = yield get_data(url)
    if cached:
        return cached
    client = tornado.httpclient.AsyncHTTPClient()
    result = yield client.fetch(url)
    if 300 >= result.code >= 200:
        yield write_data(url, result.body, options.CACHE_TIME)
    return result.body
