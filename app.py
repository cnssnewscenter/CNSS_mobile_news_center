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
        (r"/api/p/(\d*)", views.News),
        # (r"/api/column/(.*)", views.Column),
        (r"/api/index", views.Index),
        (r"/api/cache_is_evil", views.CleanCache)
    ]

    if options.DEBUG:
        route.extend([
            (r"/bower_components/(.*)", tornado.web.StaticFileHandler, {'path': "bower_components/"}),
            (r"/dist/(.*)", tornado.web.StaticFileHandler, {'path': "dist/dist/"}),
            (r"/", views.RedirectStaticFileHandler, {"path": 'static/index.html'})
        ])
    else:
        route.extend([
            (r"/dist/(.*)", tornado.web.StaticFileHandler, {'path': "dist/dist/"}),
            (r"/", views.RedirectStaticFileHandler, {"path": 'dist/index.html'})
        ])
        settings['static_path'] = os.path.join(os.path.dirname(__file__), "dist")
    application = tornado.web.Application(route, **settings)
    application.listen(8001, address="0.0.0.0")
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    config()
    runapp()
