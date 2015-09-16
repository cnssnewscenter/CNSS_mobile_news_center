import tornado.httpclient
import redis
from tornado.options import options
import tornado.gen
from tornado.log import logging


r = redis.Redis()
logger = logging.getLogger('fetcher')
logger.setLevel(logging.DEBUG)

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

    if cached and cached != "[]":
        # logging.info('CACHED %s', url)
        return cached
    client = tornado.httpclient.AsyncHTTPClient()
    result = yield client.fetch(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
    })

    if 300 >= result.code >= 200:
        yield write_data(url, result.body, options.CACHE_TIME)
    logger.debug("fetch %s, %d", url, result.code)
    return result.body
