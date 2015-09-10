import tornado.web
import fetcher
import parser
from tornado.gen import coroutine, maybe_future
import tornado.gen
import logging
import json
from tornado.options import options
import os


logger = logging.getLogger("View")


@coroutine
def get_data(url, handler):
    key = parser.convertUrl(url)
    cached = yield fetcher.get_data(key)
    if cached:
        return cached
    result = yield fetcher.get_page(url)
    ret = yield maybe_future(handler(result))
    ret = json.dumps(ret)
    yield fetcher.write_data(key, ret, options.CACHE_TIME)
    return ret


def merge(x, y):
    z = x.copy()
    z.update(y)
    return z


class News(tornado.web.RequestHandler):

    """
    单条新闻内容
    """

    @coroutine
    def get(self, pid):
        self.set_header("Content-type", 'application/json')
        url = "http://www.new1.uestc.edu.cn/?n=UestcNews.Front.Document.ArticlePage&Id="+pid
        content = yield get_data(url, parser.ParsePost)
        self.write(content)


class Index(tornado.web.RequestHandler):

    """
    板块首页
    """

    @coroutine
    def deal(self, content):
        general = parser.ParseIndexGeneral(content)

        subCategory = parser.ParseIndexSubCategory(content)
        general_link = yield [get_data(i[1], parser.ParsePost) for i in general]
        general = [merge(json.loads(general_link[i]), {"link": general[i][1]}) for i in range(len(general))]
        return {
            "general": general,
            "subCategory": subCategory
        }

    @coroutine
    def get(self):
        self.set_header("Content-type", 'application/json')
        content = yield get_data("http://www.uestc.edu.cn", self.deal)
        self.write(content)


class NewsCategory(tornado.web.RequestHandler):

    @coroutine
    def get(self):
        self.set_header("Content-type", 'application/json')
        content = yield get_data("http://www.new1.uestc.edu.cn/?n=UestcNews.Front.Category.Page&CatId=42", parser.ParseCategory)
        self.write(content)


class RedirectStaticFileHandler(tornado.web.StaticFileHandler):

    def initialize(self, path, default_filename=None):
        root, self.filename = os.path.split(path)
        super(RedirectStaticFileHandler, self).initialize(root)

    @coroutine
    def get(self, include_body=True):
        yield super(RedirectStaticFileHandler, self).get(self.filename)


class CleanCache(tornado.web.RequestHandler):

    def get(self):
        source_ip = self.request.remote_ip
        logger.warn("The redis is cleared by users: %s", source_ip)
        fetcher.r.flushdb()
        self.write("401 YOU ARE ON THE WRONG PAGE")
