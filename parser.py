from pyquery import PyQuery as pq
from lxml import html
import re
from lxml.html.clean import Cleaner
import logging
from urllib.parse import urlsplit


cleaner = Cleaner(javascript=True, scripts=True, style=True)
SinglePost = re.compile(r"http:\/\/www\.new1\.uestc\.edu\.cn\/\?n\=UestcNews\.Front\.Document\.ArticlePage\&Id\=(\d+)")
Column = re.compile(r"http:\/\/www\.new1\.uestc\.edu\.cn\/\?n\=UestcNews.Front.Category.Page&CatId=42")


logger = logging.getLogger("parser")


def makeParser(content, encoding="utf8"):
    return pq(content.decode(encoding, "ignore"))


def tostring(node):
    """
    Convert to the html string, and clean the html
    """
    return cleaner.clean_html(html.tostring(node, method="html", encoding="utf8").decode()).strip()


def convertUrl(url):
    logger.debug(url)
    if url.startswith("/") and url.split('.')[-1].lower() in ["jpg", "gif", "jpeg", "png"]:
        return "http://www.new1.uestc.edu.cn/" + url
    if "Category" in url:
        return "#/category/"+re.search("\d+", url).group()
    if "Document.ArticlePage" in url:
        return "#/post/"+re.search("\d+", url).group()
    u = urlsplit(url)
    if "www.uestc.edu.cn" == u.netloc and u.path in ["", '/']:
        return "#/"
    logger.warn("unrecognized url found: %s", url)
    return url


def ParseIndexGeneral(content):
    index = makeParser(content)
    return [(i.text_content().strip(), i.attrib['href']) for i in index(".news-left .block-content a")]


def ParseIndexSubCategory(content):
    index = makeParser(content)
    # 学术讲座、文化活动、通知公告
    return {
        "学术讲座": [(i.text_content().strip(), i.attrib['href']) for i in index(".NewsTypeScholarship a")],
        "文化活动": [(i.text_content().strip(), i.attrib['href']) for i in index(".NewsTypeHumanities a")],
        "通知公告": [(i.text_content().strip(), i.attrib['href']) for i in index(".NewsTypeNotice a")]
    }


def ParsePost(content):
    try:
        p = makeParser(content)
        title = p(".Degas_news_title").text()
        content = p(".Degas_news_content:first")[0]
        imgs = p(content).find('img')
        author = p(p(content).find('.Degas_news_info span')).text()
        author = re.sub(r"\s+", '', author.strip()).split('/')
        for i in imgs:
            if 'src' in i.attrib:
                i.attrib['src'] = convertUrl(i.attrib['src'])
        editor = [i.strip().replace('\u3000', ' ') for i in p(".Degas_news_content").next().text().split("/")]
        content = tostring(content)
        return {
            "title": title,
            "content": content,
            "author": author,
            "editor": editor
        }
    except Exception as e:
        logger.error("Oops")
        logger.exception(e)

def ParseCategory(content):
    p = makeParser(content)
    return [{
        "title": p(i).find('.h3').text().strip(),
        'link': convertUrl(p(i).find('a')[0].attrib['href']),
        'intro': p(i).find('.desc').text().strip()
    } for i in p("#Degas_news_list ul li")]
