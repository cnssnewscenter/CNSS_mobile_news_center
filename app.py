import tornado.ioloop
import tornado.web
from tornado.options import define, options, parse_config_file
import os


def config():
    define('CACHE_TIME', default=5 * 60, help="The cached time for every news, in seconds")
    define('DEBUG', default=True, help="The global debug control")

    if os.path.exists('config.py'):
        parse_config_file('config.py')
    options.log_to_stderr = False


def runapp():
    import views

    settings = {
        "debug": options.DEBUG,
        "static_path": os.path.join(os.path.dirname(__file__), "static")
    }
    route = [
        ("/api/p/(\d*)", views.News),
        ("/api/index", views.Index),
        None,
        ("/(.*)", views.RedirectStaticFileHandler, {"path": 'static/index.html'})
    ]
    if options.DEBUG:
        route[2] = ("/bower_components/(.*)", tornado.web.StaticFileHandler, {'path': "bower_components/"})
    else:
        route[2] = ("/dist/(.*)", tornado.web.StaticFileHandler, {'path': "dist/"})
    application = tornado.web.Application(route, **settings)
    application.listen(8001)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    config()
    runapp()
