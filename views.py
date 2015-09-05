import tornado.web
import fetcher
import parser
from tornado.gen import coroutine
import tornado.gen
import logging
import json
from tornado.options import options
import os


logger = logging.getLogger("View")


@coroutine
def get_data(self, url, handler):
    key = parser.convertUrl(url)
    cached = yield fetcher.get_data(key)
    if cached:
        return cached
    result = yield fetcher.get_page(url)
    ret = json.dumps(handler(result))
    yield fetcher.write_data(key, ret, options.CACHE_TIME)
    return ret


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
        for n, i in enumerate(general):
            general[n] = yield get_data(i[1])

        return {
            "general": general,
            "subCategory": subCategory
        }

    @coroutine
    def get(self):
        self.set_header("Content-type", 'application/json')
        content = yield get_data("#/", self.deal)
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
