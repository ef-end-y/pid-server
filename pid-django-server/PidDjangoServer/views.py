import json
import random
import string
from os import path, listdir
from subprocess import Popen

from django.conf import settings
from django.shortcuts import render
from django.http import Http404, FileResponse
from annoying.decorators import render_to


@render_to('index.html')
def _index(request, error='', noise_bounds=settings.NOISE_BOUNDS):
    assert request
    return {
        'noise_bounds': noise_bounds,
        'error': error,
    }


def index(request):
    return _index(request)


def upload_bbl(request):
    noise_bounds = request.POST.get('noise_bounds', settings.NOISE_BOUNDS)
    bbl_content = request.FILES.get('bbl_file')
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

    bbl_content = bbl_content.file.read()

    bbl_file = path.join(settings.PROJECT_PATH, 'files/%s.bbl' % job_id)
    with open(bbl_file, 'wb') as file:
        file.write(bbl_content)

    log_file = path.join(settings.PROJECT_PATH, 'files/%s.log' % job_id)

    cmd = [
        settings.PID_ANALYZER_PATH,
        '-l', bbl_file,
        '-n', job_id,
        '--blackbox_decode', settings.BLACKBOX_DECODER_PATH,
        '-s', 'N',
        '-nb', noise_bounds
    ]

    with open(log_file, 'w') as log:
        Popen(cmd, stderr=log, stdout=log)

    return render(request, 'result.html', {
        'result': 'In progress ...',
        'job_id': job_id,
        'step': 0,
        'files': 0,
        'log': ''
    })

def result(request):
    job_id = str(request.GET.get('job_id'))

    log_file = path.join(settings.PROJECT_PATH, 'files/%s.log' % job_id)
    with open(log_file, 'r') as file:
        log_content = file.read()

    try:
        step = int(request.GET.get('step')) + 1
        assert step > 0
    except:
        step = 1

    if step < 2:
        # PID Analyzer needs time for dir creation
        files = []
    else:
        p = _path_by_job_id(job_id)
        if not p:
            raise Http404()
        files = [f for f in listdir(p) if f.endswith('.png') and path.isfile(path.join(p, f))]

    if 'Analysis complete' not in log_content and step < 40:

        return render(request, 'result.html', {
            'result': 'In progress ' + '.' * (step+3),
            'job_id': job_id,
            'step': step,
            'files': len(files),
            'log': log_content
        })

    return render(request, 'result_ok.html', {
        'job_id': job_id,
        'files': files,
        'log': log_content
    })


def download(request, job_id, file):
    p = _path_by_job_id(job_id)
    if not p:
        raise Http404()

    if not file.endswith('.png') or not file[0:-4].replace('_', '').isalnum():
        raise Http404()

    file = path.join(settings.PROJECT_PATH, 'files', job_id, file)

    return FileResponse(open(file, 'rb'))



def _path_by_job_id(job_id):
    if len(job_id) != 12 and not job_id.isalpha():
        return None
    p = path.join(settings.PROJECT_PATH, 'files', job_id)
    if not path.exists(p) or not path.isdir(p):
        return None
    return p
