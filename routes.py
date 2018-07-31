#! -*- coding: utf-8 -*-
import views


routes = {
    ('*', '', views.index, 'index'),
    ('*', '/upload_bbl', views.upload_bbl, 'upload_bbl'),
    ('*', '/result', views.result, 'result'),
    ('*', '/download', views.download, 'download'),

}


def setup(app):
    for route in routes:
        app.router.add_route(*route[0:3], name=route[3])
