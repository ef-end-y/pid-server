#! -*- coding: utf-8 -*-
import os
import json
import string
import random
import asyncio
from subprocess import Popen
from aiohttp import web


from settings import PROJECT_PATH, NOISE_BOUNDS, PAGES


def _make_html(body):
    return PAGES['html'].format(body=body, css=PAGES['css'])


def _error(error):
    return PAGES['error'].format(error=error)


def _path_by_job_id(job_id):
    if len(job_id) != 12 and not job_id.isalpha():
        return None
    path = os.path.join(PROJECT_PATH, 'files', job_id)
    if not os.path.exists(path) or not os.path.isdir(path):
        return None
    return path


def _index(request, error='', noise_bounds=NOISE_BOUNDS):
    page = PAGES['index']
    if error is not None:
        error = _error(error)
    page = page.format(
        url=request.app.router['upload_bbl'].url_for(),
        noise_bounds=noise_bounds,
        error=error,
    )
    return web.Response(
        content_type='text/html',
        text=_make_html(page),
    )


async def index(request):
    return _index(request)


async def upload_bbl(request):
    if request.method == 'GET':
        return _index(request)

    data = await request.post()
    noise_bounds = data.get('noise_bounds', NOISE_BOUNDS)
    bbl_content = data.get('bbl_file')
    if not bbl_content or not hasattr(bbl_content, 'file'):
        return _index(request, 'You need to select bbl-file', noise_bounds)

    try:
        nb = json.loads(noise_bounds)
        assert isinstance(nb, list)
        for i in nb:
            assert isinstance(i, list)
            for j in i:
                assert isinstance(j, float)
    except:
        return _index(request, 'Wrong format of noise bounds', noise_bounds)
    noise_bounds = json.dumps(nb)

    job_id = ''.join(random.choice(string.ascii_letters) for _ in range(12))

    app = request.app
    asyncio.ensure_future(
        _analysis(job_id, bbl_content, noise_bounds, app.pid_analyzer_path, app.blackbox_decoder_path)
    )

    page = PAGES['result'].format(
        result='In progress ...',
        result_url=request.app.router['result'].url_for(),
        job_id=job_id,
        step=0,
        files=0,
        log=''
    )

    return web.Response(
        content_type='text/html',
        text=_make_html(page),
    )


async def _analysis(job_id, bbl_content, noise_bounds, pid_analyzer_path, blackbox_decoder_path):
    bbl_content = bbl_content.file.read()

    bbl_file = os.path.join(PROJECT_PATH, 'files/%s.bbl' % job_id)
    with open(bbl_file, 'wb') as file:
        file.write(bbl_content)

    log_file = os.path.join(PROJECT_PATH, 'files/%s.log' % job_id)

    cmd = [
        pid_analyzer_path,
        '-l', bbl_file,
        '-n', job_id,
        '--blackbox_decode', blackbox_decoder_path,
        '-s', 'N',
        '-nb', noise_bounds
    ]

    with open(log_file, 'w') as log:
        Popen(cmd, stderr=log, stdout=log)


async def result(request):
    job_id = str(request.rel_url.query.get('job_id'))

    log_file = os.path.join(PROJECT_PATH, 'files/%s.log' % job_id)
    with open(log_file, 'r') as file:
        log_content = file.read()

    try:
        step = int(request.rel_url.query['step']) + 1
        assert step > 0
    except:
        step = 1

    if step < 2:
        # PID Analyzer needs time for dir creation
        files = []
    else:
        path = _path_by_job_id(job_id)
        if not path:
            return web.Response(status=404)
        files = [f for f in os.listdir(path) if f.endswith('.png') and os.path.isfile(os.path.join(path, f))]

    if 'Analysis complete' not in log_content and step < 40:

        page = PAGES['result'].format(
            result='In progress ' + '.' * (step+3),
            result_url=request.app.router['result'].url_for(),
            job_id=job_id,
            step=step,
            files=len(files),
            log=log_content
        )
        return web.Response(
            content_type='text/html',
            text=_make_html(page),
        )

    files = '<hr>'.join(["<img src='/download?id=%s&file=%s'>" % (job_id, i) for i in files])
    page = PAGES['result_ok'].format(
        files=files,
        index_url=request.app.router['index'].url_for(),
        log=log_content
    )
    return web.Response(
        content_type='text/html',
        text=_make_html(page),
    )


async def download(request):
    job_id = str(request.rel_url.query.get('id'))
    path = _path_by_job_id(job_id)
    if not path:
        return web.Response(status=404)

    file = str(request.rel_url.query.get('file'))
    if not file.endswith('.png') or not file[0:-4].replace('_', '').isalnum():
        return web.Response(status=404)

    file = os.path.join(PROJECT_PATH, 'files', job_id, file)

    return web.FileResponse(file)
