import tornado.web
import fetcher
import parser
from parser import convertUrl
from tornado.gen import coroutine, maybe_future
import tornado.gen
import tornado.httpclient
import logging
import json
from tornado.options import options
import os
from tornado.httpclient import HTTPError


logger = logging.getLogger("View")
if options.DEBUG:
    logger.setLevel(logging.DEBUG)


@coroutine
def get_data(url, handler):
    key = parser.convertUrl(url)
    if not options.DEBUG:
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


def makeUrl(type, **kwargs):

    logger.debug("make url %s, %s", type, kwargs)

    if "post" == type:
        return "http://www.news.uestc.edu.cn/?n=UestcNews.Front.Document.ArticlePage&Id={Id}".format_map(kwargs)
    elif "category" == type:
        kwargs['page'] = kwargs.get("page", "1")
        return "http://www.news.uestc.edu.cn/?n=UestcNews.Front.Category.Page&CatId={CatId}&page={page}".format_map(kwargs)
    elif "index" == type:
        return "http://www.uestc.edu.cn"
    else:
        logger.warn("unknown type")
        raise NotImplemented


class BaseHandler(tornado.web.RequestHandler):

    def _handle_request_exception(self, e):
        if isinstance(e, tornado.httpclient.HTTPError):
            if self._finished:
                return
            else:
                self.clear()
                self.write_error(502, json.dumps({
                    "err": "502",
                    "msg": "请求太快啦！",
                    "raw_msg": str(e)
                }))
                logging.error("Fail to task to upstream")
        else:
            super(BaseHandler, self)._handle_request_exception(e)


class News(tornado.web.RequestHandler):

    """
    单条新闻内容
    """

    @coroutine
    def get(self, pid):
        self.set_header("Content-type", 'application/json')
        url = makeUrl('post', Id=pid)
        content = yield get_data(url, parser.ParsePost)
        self.write(content)


class Index(tornado.web.RequestHandler):

    """
    首页
    轮播图数据来自于焦点新闻（有图的）
    下方新闻来自于首页的新闻汇总
    """

    @coroutine
    def deal(self, content):

        def compact(l):
            ret = []
            for i in l:
                ret += i
            return ret
        general = parser.ParseIndexGeneral(content)

        tries = 4
        while tries > 0:
            try:
                news = yield [get_data(i[1], parser.ParsePost) for i in general['news']]
                info = yield [get_data(makeUrl('category', CatId=i), parser.ParseCategory) for i in [66, 67, 68]]

                ret = {
                    "news": [json.loads(i) for i in news],
                    "info": compact([json.loads(i)[:4] for i in info]),
                }
                break
            except HTTPError:
                tries -= 1
                print("503, Retry.....")
                yield tornado.gen.sleep(.1)
                continue

        for n, i in enumerate(ret['news']):
            i["link"] = convertUrl(general["news"][n][1], strict=True)
        return ret

    @coroutine
    def get(self):
        self.set_header("Content-type", 'application/json')
        content = yield [get_data(makeUrl("index"), self.deal), get_data(makeUrl("category", CatId=42), parser.ParseCategory)]
        index = json.loads(content[0])
        ret = {
            "news": index["news"],
            "info": index["info"],
            "slide": json.loads(content[1]),
        }
        self.write(json.dumps(ret))


class NewsCategory(tornado.web.RequestHandler):

    @coroutine
    def get(self, cid):
        self.set_header("Content-type", 'application/json')
        page = self.get_argument('page', '1')
        content = yield get_data(makeUrl('category', page=page, CatId=cid), parser.ParseCategory)
        self.write(content)


class RedirectStaticFileHandler(tornado.web.StaticFileHandler):

    def initialize(self, path):
        root, self.filename = os.path.split(path)
        super(RedirectStaticFileHandler, self).initialize(root)

    @coroutine
    def get(self, include_body=True):
        yield super(RedirectStaticFileHandler, self).get(self.filename, include_body)


class CleanCache(tornado.web.RequestHandler):

    def get(self):
        source_ip = self.request.remote_ip
        logger.warn("The redis is cleared by users: %s", source_ip)
        fetcher.r.flushdb()
        self.write("缓存已经清空")
