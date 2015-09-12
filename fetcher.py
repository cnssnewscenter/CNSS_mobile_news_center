import tornado.httpclient
import redis
from tornado.options import options
import tornado.gen
from tornado.log import logging

r = redis.Redis()


@tornado.gen.coroutine
def get_data(key):
    """
    return None or the data in the redis cache
    """
    global r
    try:
        cached = r.get(key)
        return cached.decode() if cached else None
    except Exception as e:
        logging.exception(e)
        logging.warn('Fail to connect to the redis cache server')
        return None


@tornado.gen.coroutine
def write_data(key, value, timeout):
    global r
    try:
        r.setex(key, value, timeout)
    except Exception as e:
        logging.exception(e)
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
