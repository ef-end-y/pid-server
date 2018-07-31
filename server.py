#! -*- coding: utf-8 -*-
from aiohttp import web
import click

import routes
import settings

@click.command()
@click.option('-H', '--host', default='localhost', help='TCP/IP hostname to serve on')
@click.option('-P', '--port', default=9099, help='TCP/IP port to serve on')
@click.option('-A', '--ppath', default=settings.PID_ANALYZER_PATH, help='Path to PID-Analyzer.py')
@click.option('-B', '--bpath', default=settings.BLACKBOX_DECODER_PATH, help='Path to blackbox_decode')
def run_server(host, port, ppath, bpath):
    app = web.Application(client_max_size=16*1024*1024)
    app.pid_analyzer_path = ppath
    app.blackbox_decoder_path = bpath
    routes.setup(app)
    web.run_app(app=app, host=host, port=port)


if __name__ == '__main__':
    run_server()
