import tornado.web
import fetcher
from tornado.gen import coroutine
import tornado.gen
from lxml import html
import re
import json
from lxml.html.clean import Cleaner
from tornado.options import options
import os

cleaner = Cleaner(javascript=True, scripts=True, style=True)


def addQueue(url):
    if url.startswith("/"):
        return "http://www.new1.uestc.edu.cn/" + url
    else:
        return url


def tostring(node):
    """
    转换元素节点为字符串，并清理 HTML 标签
    """
    return cleaner.clean_html(html.tostring(node, method="html", encoding="utf8").decode()).strip()


def makeParser(ubytes):
    return html.document_fromstring(ubytes.decode("utf8"))


class News(tornado.web.RequestHandler):
    """
    单条新闻内容
    """
    @coroutine
    def gen(self, pid):

        url = "http://www.new1.uestc.edu.cn/?n=UestcNews.Front.Document.ArticlePage&Id={}".format(pid)
        result = yield fetcher.get_page(url)
        tree = makeParser(result)
        title = tree.xpath('//h1')[0].text_content()
        content = tree.xpath('//div[@class="Degas_news_content"]')[0]
        imgs = content.findall('.//img')
        author = content.xpath('//div[@class="Degas_news_info"]/span/text()')[0]
        author = re.sub(r"\s+", '', author.strip()).split('/')
        for i in imgs:
            if 'src' in i.attrib:
                i.attrib['src'] = addQueue(i.attrib['src'])
        editor = [i.strip() for i in content.getnext().text_content().strip().split("/")]
        content = tostring(content)
        return json.dumps({
            "title": title,
            "content": content,
            "author": author,
            "editor": editor
        })

    @coroutine
    def get(self, pid):
        self.set_header("Content-type", 'application/json')
        source = "local/api/p/{}".format(pid)
        if fetcher.caching:
            cached = fetcher.r.get(source)
            if cached:
                self.write(cached)
                return
        content = yield self.gen(pid)
        fetcher.r.setex(source, content, options.CACHE_TIME)
        self.write(content)


class Index(tornado.web.RequestHandler):
    """
    板块首页
    """

    def translateLink(self, link):
        return link

    @coroutine
    def gen(self):
        result = {}
        # 综合新闻、三个分栏目
        school_index = yield fetcher.get_page('http://www.uestc.edu.cn/')
        general_news = makeParser(school_index)
        # 综合新闻
        result['general'] = [(i.text_content().strip(), i.attrib['href']) for i in general_news.xpath("//div[@class='news-left']//div[@class='block-content']//a")]
        # 学术讲座、文化活动、通知公告
        result['sub_col'] = {
            "学术讲座": [(i.text_content().strip(), i.attrib['href']) for i in general_news.xpath("//div[contains(@class, 'NewsTypeScholarship')]//a")],
            "文化活动": [(i.text_content().strip(), i.attrib['href']) for i in general_news.xpath("//div[contains(@class, 'NewsTypeHumanities')]//a")],
            "通知公告": [(i.text_content().strip(), i.attrib['href']) for i in general_news.xpath("//div[contains(@class, 'NewsTypeNotice')]//a")]
        }
        # 焦点新闻
        top_news_index = yield fetcher.get_page('http://www.new1.uestc.edu.cn/?n=UestcNews.Front.Category.Page&CatId=42')
        top_news_index = makeParser(top_news_index)
        # 返回前十条
        result['top'] = [{"title": i.find('.//h3').text_content().strip(), 'link': i.find('.//a').attrib['href'], 'intro': i.find('.//p[@class="desc"]').text_content().strip()} for i in top_news_index.xpath("//div[@id='Degas_news_list']/ul/li")[:10]]  # todo extract the magic number
        return json.dumps(result)

    @coroutine
    def get(self):
        self.set_header("Content-type", 'application/json')
        if fetcher.caching:
            cached = fetcher.r.get('local/index')
            if cached:
                self.write(cached)
                return
        content = yield self.gen()
        fetcher.r.setex('local/index', content, options.CACHE_TIME)
        self.write(content)



class NewsCatalog(tornado.web.RequestHandler):

    @coroutine
    def gen(self):
        news = yield fetcher.get_page('http://www.new1.uestc.edu.cn/?n=UestcNews.Front.Category.Page&CatId=42')
        news = makeParser(news)
        result = [{"title": i.find('.//h3').text_content().strip(), 'link': i.find('.//a').attrib['href'], 'intro': i.find('.//p[@class="desc"]').text_content().strip()} for i in top_news_index.xpath("//div[@id='Degas_news_list']/ul/li")[:10]]
        return json.dumps(result)

    @coroutine
    def get(self):
        self.set_header("Content-type", 'application/json')
        if fetcher.caching:
            cached = fetcher.r.get('local/index')
            if cached:
                self.write(cached)
                return
        content = yield self.gen()
        fetcher.r.setex('local/index', content, options.CACHE_TIME)
        self.write(content)


class RedirectStaticFileHandler(tornado.web.StaticFileHandler):

    def initialize(self, path, default_filename=None):
        root, self.filename = os.path.split(path)
        super(RedirectStaticFileHandler, self).initialize(root)

    @coroutine
    def get(self, include_body=True):
        yield super(RedirectStaticFileHandler, self).get(self.filename)
