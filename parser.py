from pyquery import PyQuery as pq
from lxml import html

import re
from lxml.html.clean import Cleaner
import logging
from urllib.parse import urlsplit, parse_qs


cleaner = Cleaner(javascript=True, scripts=True, style=True)
SinglePost = re.compile(r"http:\/\/www\.news\.uestc\.edu\.cn\/\?n\=UestcNews\.Front\.Document\.ArticlePage\&Id\=(\d+)")
Column = re.compile(r"http:\/\/www\.news\.uestc\.edu\.cn\/\?n\=UestcNews.Front.Category.Page&CatId=42")


logger = logging.getLogger("parser")


def makeParser(content, encoding="utf8"):
    content = content.decode(encoding, "ignore") if isinstance(content, bytes) else str(content)
    return pq(content)


def tostring(node):
    """
    Convert to the html string, and clean the html
    """
    return cleaner.clean_html(html.tostring(node, method="html", encoding="utf8").decode()).strip()


def convertUrl(url, strict=False):
    logger.debug(url)
    if not url:
        return None
    if "http://www.news.uestc.edu.cn/" == url:
        return "index_2"
    if url.startswith("/upload"):
        return "http://www.news.uestc.edu.cn" + url
    # try to parse
    u = urlsplit(url)
    if "/?" in url:

        data = parse_qs(u.query)
        if data.get('n')[0] == "UestcNews.Front.Category.Page":
            return "/category/"+data.get("CatId")[0]+"?page="+data.get('page', ["1"])[0]
        if data.get("n")[0] == "UestcNews.Front.Document.ArticlePage":
            return "/post/"+data.get("Id")[0]

    if "www.uestc.edu.cn" == u.netloc and u.path in ["", '/']:
        return "/"
    logger.warn("unrecognized url found: %s", url)
    if strict:
        return None
    return url


def ParseIndexGeneral(content):
    index = makeParser(content)
    return {
        "news": [(i.text_content().strip(), i.attrib['href']) for i in index(".news-left .news-block").eq(0).find(".block-content a") if convertUrl(i.attrib['href'], True)],
        "info": [(i.text_content().strip(), i.attrib['href']) for i in index(".news-left .news-block").eq(1).find(".block-content a") if convertUrl(i.attrib['href'], True)],
    }


# def ParseIndexSubCategory(content):
#     index = makeParser(content)
#     # 学术讲座、文化活动、通知公告
#     return {
#         "学术讲座": [(i.text_content().strip(), i.attrib['href']) for i in index(".NewsTypeScholarship a")],
#         "文化活动": [(i.text_content().strip(), i.attrib['href']) for i in index(".NewsTypeHumanities a")],
#         "通知公告": [(i.text_content().strip(), i.attrib['href']) for i in index(".NewsTypeNotice a")]
#     }


def ParsePost(content):
    try:
        p = makeParser(content)
        title = p(".Degas_news_title").text()
        content = p(".Degas_news_content:first")[0]
        imgs = p(content).find('img')
        collectd = []
        for i in imgs:
            if 'src' in i.attrib:
                i.attrib['src'] = convertUrl(i.attrib['src'])
                collectd.append(i.attrib['src'])
        for i in p(content).find("a[href^=/upload]"):
            i.attrib['href'] = convertUrl(i.attrib['href'])
        editor = [i.strip().replace('\u3000', ' ') for i in p(".Degas_news_content").next().text().split("/")]
        content = tostring(content)
        info = [re.sub(r"\s+", " ", i.strip()) for i in p('.Degas_news_info').text().split("/")]
        sub = p('#Degas_news_list > h3').text().strip() if p('#Degas_news_list > h3') else None
        return {
            "title": title,
            "content": content,
            "author": info[0],
            "authors": list(filter(lambda x: ":" in x or "：" in x, info)),
            "editor": editor,
            "img": collectd,
            "date": info[2],
            "sub_title": sub
        }
    except Exception as e:
        logger.error("Oops")
        logger.exception(e)


def strip_text(e):
    if e is not None:
        return e.text().strip()
    else:
        return ""


def ParseCategory(content):
    p = makeParser(content)
    ret = []
    for i in p("#Degas_news_list ul:first li"):
        i = p(i)
        link = i.find("a").attr('href')
        if link and "ArticlePage" in link:
            ret.append({
                "title": strip_text(i.find('h3')),
                'link': convertUrl(i.find('a').attr('href')),
                'intro': strip_text(i.find('.desc')),
                "img": convertUrl(i.find('img').attr('src'))
            })
    return ret


def ParseSlider(content):
    p = makeParser(content)
    ret = []
    for i in p('#slide_list li'):
        i = p(i)
        ret.append({
            "title": i.find('h2').text().strip(),
            "img": convertUrl(i.find('img').attr('src')),
            "link": convertUrl(i.find('a').attr("href"))
        })
    return ret
